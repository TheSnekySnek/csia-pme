import asyncio
import io

import httpx
import numpy as np
import logging
import pandas as pd
from adtk.detector import GeneralizedESDTestAD
from io import StringIO
import tensorflow as tf
from matplotlib import pyplot as plt


class Worker():
    def __init__(self):
        self.asyncTask = None
        self.running = False
        self.queue = asyncio.Queue()
        self.next = None

    def start(self):
        self.running = True
        self.asyncTask = asyncio.create_task(self.run())

    def chain(self, worker):
        self.next = worker

    async def stop(self):
        self.running = False
        await self.queue.put(None)
        await self.asyncTask

    async def addTask(self, task):
        await self.queue.put(task)

    async def run(self):
        while self.running:
            task = await self.queue.get()
            if task is not None:
                result = await self.process(task)
                if result is not None and self.next is not None:
                    await self.next.addTask(result)

    async def process(self, task):
        try:
            raw = task["text"].file
            df = pd.read_csv(raw, names=["value"])
            # df.index = pd.to_datetime(df.index)
            # esd_ad = GeneralizedESDTestAD(alpha=0.3)
            # anomalies = esd_ad.fit_detect(df["value"])
            # condition = anomalies == True
            X_train = df[0:12000].to_numpy()
            X_test = df[12000:].to_numpy()
            # indexes = anomalies.index[condition]
            # result = indexes.strftime("%Y-%m-%d %H:%M:%S.%f").tolist()
            autoencoder = self.train_model(X_train)
            # Use the model to reconstruct the original time series data
            reconstructed_X = autoencoder.predict(X_test)

            # Calculate the reconstruction error for each point in the time series
            reconstruction_error = np.square(X_test - reconstructed_X).mean(axis=1)

            # Data points with a high reconstruction error are likely to be anomalies
            anomalies = np.where(reconstruction_error > 1)[0].tolist()

            err = pd.DataFrame(X_test)
            fig, ax = plt.subplots(figsize=(20, 6))

            a = err.loc[reconstruction_error > 0.5]  # anomaly
            # b = np.arange(35774-12000, 35874-12000)
            ax.plot(err, color='blue', label='Normal')

            # ax.scatter(b, err[35774-12000:35874-12000], color='green', label = 'Real anomaly')
            ax.scatter(a.index, a, color='red', label='Anomaly')
            plt.legend()
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            print(a)

            # shape = self.model.input.shape[1]
            # sz = int(np.sqrt(shape))
            # resized = cv2.resize(img, (sz, sz))
            # normalized = resized / 255.0
            # flattened = np.reshape(normalized, [-1, shape])
            # pred = self.model.predict(flattened)
            # guessed = np.argmax(pred)
            task["result"] = {"image": buf.read()}
        except Exception as e:
            task["error"] = f"Yo to process image: {str(e)}"
        # print(str(e))

        return task

    def train_model(self, X_train):
        # Preprocess the data (e.g., scale the data, create train/test splits)

        # Define the input layer
        input_layer = tf.keras.layers.Input(shape=(X_train.shape[1],))

        # Define the encoding layers
        encoded = tf.keras.layers.Dense(32, activation='relu')(input_layer)
        encoded = tf.keras.layers.Dense(16, activation='relu')(encoded)

        # Define the decoding layers
        decoded = tf.keras.layers.Dense(16, activation='relu')(encoded)
        decoded = tf.keras.layers.Dense(32, activation='relu')(decoded)

        # Define the output layer
        output_layer = tf.keras.layers.Dense(X_train.shape[1])(decoded)

        # Create the autoencoder model
        autoencoder = tf.keras.models.Model(input_layer, output_layer)

        # Compile the model
        autoencoder.compile(optimizer='adam', loss='mean_squared_error')

        # Fit the model to the time series data
        autoencoder.fit(X_train, X_train, epochs=10, batch_size=32)

        return autoencoder





class Callback(Worker):
    def __init__(self):
        super().__init__()
        self.client = httpx.AsyncClient(timeout=30.0)

    async def process(self, task):
        url = task["callback_url"]
        task_id = task["task_id"]
        if url is not None:
            data = None
            if "error" in task:
                data = {"type": "error", "message": task["error"]}
            else:
                data = task["result"]
            try:
                await self.client.post(url, params={"task_id": task_id}, files=data)
            except Exception as e:
                logging.getLogger("uvicorn").warning("Failed to send back result (" + url + "): " + str(e))
