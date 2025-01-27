import React from 'react';
import {
    Box,
    Button,
    Card,
    CardActions,
    CardContent,
    Chip,
    CircularProgress,
    Divider,
    FormControl,
    InputLabel,
    MenuItem,
    Pagination,
    Select,
    Tooltip,
    Typography
} from '@mui/material';
import Grid from '@mui/material/Unstable_Grid2';
import { getPipelines, getServices } from '../../utils/api';
import { Link, useSearchParams } from 'react-router-dom';
import { useNotification } from '../../utils/useNotification';
import "./styles.css";
import { Tags } from '../../enums/tagEnums';
import { Tag } from '../../models/Tag';
import { useDispatch, useSelector } from 'react-redux';
import { setServicePerPage, setPipelinePerPage } from '../../utils/reducers/perPageSlice';

// min width is 100% for mobile, 50% for tablet, 33% for desktop
const minWidth = (window.innerWidth < 600) ? '100%' : (window.innerWidth < 900) ? '50%' : '33%';

// align center for mobile, left for tablet and desktop
const align = (window.innerWidth < 600) ? 'center' : 'left';

const ItemGrid: React.FC<{
    filter: string, orderBy: string, tags: Tag[]
}> = ({filter, orderBy, tags}) => {
    const dispatch = useDispatch();
    const servicesPerPage = useSelector((state: any) => state.perPage.value.services);
    const pipelinesPerPage = useSelector((state: any) => state.perPage.value.pipelines);
    const [serviceCount, setServiceCount] = React.useState(0);
    const [pipelineCount, setPipelineCount] = React.useState(0);
    const [pageService, setPageService] = React.useState(1);
    const [pagePipeline, setPagePipeline] = React.useState(1);
    const [isReady, setIsReady] = React.useState(false);
    const [searchParams] = useSearchParams();
    const [pipelines, setPipelines] = React.useState([]);
    const [services, setServices] = React.useState([]);
    const {displayNotification} = useNotification();

    const setServicesPerPage = (value: number) => {
        setPageService(1);
        dispatch(setServicePerPage(value));
    };

    const setPipelinesPerPage = (value: number) => {
        setPagePipeline(1);
        dispatch(setPipelinePerPage(value));
    }

    const listServices = async (filter: string, orderBy: string, tags: string[]) => {
        const skip = (pageService - 1) * servicesPerPage;
        const servicesList = await getServices(filter, skip, servicesPerPage, orderBy, tags);
        if (servicesList) {
            setServices(servicesList.services);
            setServiceCount(servicesList.count);
        } else {
            setServices([]);
            setServiceCount(0);
            displayNotification({message: "No services found", type: "info"});
        }
    }

    const listPipelines = async (filter: string, orderBy: string, tags: string[]) => {
        const skip = (pagePipeline - 1) * pipelinesPerPage;
        const pipelinesList = await getPipelines(filter, skip, pipelinesPerPage, orderBy, tags);
        if (pipelinesList) {
            setPipelines(pipelinesList.pipelines);
            setPipelineCount(pipelinesList.count);
        } else {
            setPipelines([]);
            setPipelineCount(0);
            displayNotification({message: "No pipelines found", type: "info"});
        }
    }

    const listElements = async (filter: string, orderBy: string, tags: string[]) => {
        await listServices(filter, orderBy, tags);
        await listPipelines(filter, orderBy, tags);
        setIsReady(true);
    }

    const servicePagination = () => {
        return (
            <Grid container spacing={4} alignItems={"center"} justifyContent={"center"}>
                <Grid xs={12} md={6} lg={4} alignItems={"left"} justifyContent={"left"}>
                    <Box sx={{display: 'flex', alignItems: align, justifyContent: align}}>
                        <Pagination
                            page={pageService}
                            size={"large"}
                            onChange={(event, page) => {
                                setPageService(page);
                            }}
                            sx={{alignItems: 'center', justifyContent: 'center'}}
                            count={Math.ceil(serviceCount / servicesPerPage)}
                            shape={"rounded"}
                        />
                    </Box>
                </Grid>
                <Grid xs={12} md={6} lg={4} mdOffset={"auto"} alignItems={"right"} justifyContent={"right"}>
                    <Box sx={{display: 'flex', alignItems: 'right', justifyContent: 'right'}}>
                        <FormControl sx={{minWidth: minWidth}}>
                            <InputLabel id={"services-per-page-label"}>Per page</InputLabel>
                            <Select
                                labelId={"services-per-page"}
                                id={"services-per-page"}
                                value={servicesPerPage}
                                label={"Per page"}
                                onChange={(event) => {
                                    setServicesPerPage(event.target.value as number);
                                }}
                            >
                                <MenuItem value={6}>6</MenuItem>
                                <MenuItem value={15}>15</MenuItem>
                                <MenuItem value={30}>30</MenuItem>
                                <MenuItem value={60}>60</MenuItem>
                            </Select>
                        </FormControl>
                    </Box>
                </Grid>
            </Grid>
        );
    };

    const pipelinePagination = () => {
        return (
            <Grid container sx={{pt: 2}} spacing={4} alignItems={"center"} justifyContent={"center"}>
                <Grid xs={12} md={6} lg={4} alignItems={"left"} justifyContent={"left"}>
                    <Box sx={{display: 'flex', alignItems: align, justifyContent: align}}>
                        <Pagination
                            page={pagePipeline}
                            size={"large"}
                            onChange={(event, page) => {
                                setPagePipeline(page);
                            }}
                            sx={{alignItems: 'center', justifyContent: 'center'}}
                            count={Math.ceil(pipelineCount / pipelinesPerPage)}
                            shape={"rounded"}
                        />
                    </Box>
                </Grid>
                <Grid xs={12} md={6} lg={4} mdOffset={"auto"} alignItems={"right"} justifyContent={"right"}>
                    <Box sx={{display: 'flex', alignItems: 'right', justifyContent: 'right'}}>
                        <FormControl sx={{minWidth: minWidth}}>
                            <InputLabel id={"pipelines-per-page-label"}>Per page</InputLabel>
                            <Select
                                labelId={"pipelines-per-page"}
                                id={"pipelines-per-page"}
                                value={pipelinesPerPage}
                                label={"Per page"}
                                onChange={(event) => {
                                    setPipelinesPerPage(event.target.value as number);
                                }}
                            >
                                <MenuItem value={6}>6</MenuItem>
                                <MenuItem value={15}>15</MenuItem>
                                <MenuItem value={30}>30</MenuItem>
                                <MenuItem value={60}>60</MenuItem>
                            </Select>
                        </FormControl>
                    </Box>
                </Grid>
            </Grid>
        );
    };

    React.useEffect(() => {
        setIsReady(false);
        setPageService(1);
        setPagePipeline(1);
        listElements(filter, orderBy, tags.map(t => t.acronym));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [servicesPerPage, pipelinesPerPage]);

    React.useEffect(() => {
        setIsReady(false);
        listElements(filter, orderBy, tags.map(t => t.acronym));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [pageService, pagePipeline, orderBy, tags]);

    React.useEffect(() => {
        // on filter change, use listElements to update the list only if the user stopped typing for 1000ms
        const timeout = setTimeout(() => {
            setIsReady(false);
            setPageService(1);
            setPagePipeline(1);
            listElements(filter, orderBy, tags.map(t => t.acronym));
        }, 300);
        return () => clearTimeout(timeout);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [filter]);

    return (
        <>
            <Typography gutterBottom variant={"h4"} component={"h2"}>
                Services
            </Typography>
            {isReady && services.length > 0 ?
                servicePagination() : <></>
            }
            {!isReady ?
                <Grid xs={12} md={8} sx={{textAlign: 'center'}}>
                    <CircularProgress/>
                </Grid>
                :
                <Grid container spacing={4}>
                    {services.length === 0 ? (
                        <Grid xs={6} md={8}>
                            <Typography gutterBottom variant={"h6"} component={"h2"}>
                                No service found
                            </Typography>
                        </Grid>
                    ) : (
                        services.map((item: any, index: number) => {
                                return (
                                    <Grid xs={12} sm={6} xl={4} key={index}
                                          sx={{height: 'auto', minHeight: '200px'}}>
                                        <Card
                                            sx={{height: '100%', display: 'flex', flexDirection: 'column'}}
                                        >
                                            <CardContent sx={{flexGrow: 1}}>
                                                <Typography variant="h5" component="h2" gutterBottom>
                                                    {item.name}
                                                </Typography>
                                                <Grid container spacing={1} sx={{p: 0, mb: 2}}>
                                                    {item.tags ? item.tags.map((tag: any, index: number) => {
                                                        return (
                                                            <Grid key={`service-tag-${index}`}>
                                                                <Tooltip title={tag.name}>
                                                                    <Chip
                                                                        className={"acronym-chip"}
                                                                        label={tag.acronym}
                                                                        style={
                                                                            Tags.filter((t) =>
                                                                                t.acronym === tag.acronym)[0].colors
                                                                        }
                                                                        variant="outlined"
                                                                        size={"small"}
                                                                    />
                                                                </Tooltip>
                                                            </Grid>
                                                        )
                                                    }) : ''}
                                                </Grid>
                                                <Typography>
                                                    {
                                                        item.summary.length > 80 ?
                                                            item.summary.substring(0, 75) + "..." :
                                                            item.summary
                                                    }
                                                </Typography>
                                            </CardContent>
                                            <CardActions sx={{p: 2}}>
                                                <Link
                                                    to={"/showcase/service/" + item.id}>
                                                    <Button size={"small"} variant={"contained"}>View</Button>
                                                </Link>
                                            </CardActions>
                                        </Card>
                                    </Grid>
                                )
                                    ;
                            }
                        ))}
                </Grid>
            }
            {isReady && services.length > 0 ?
                servicePagination() : <></>
            }
            <Divider sx={{mt: 2, mb: 2}}>
                ○
            </Divider>
            <Typography gutterBottom variant={"h4"} component={"h2"}>
                Pipelines
            </Typography>
            {isReady && pipelines.length > 0 ?
                pipelinePagination() : <></>
            }
            {!isReady ?
                <Grid xs={12} md={8} sx={{textAlign: 'center'}}>
                    <CircularProgress/>
                </Grid>
                :
                <Grid container spacing={4}>
                    {pipelines.length === 0 ? (
                        <Grid xs={6} md={8}>
                            <Typography gutterBottom variant={"h6"} component={"h2"}>
                                No pipeline found
                            </Typography>
                        </Grid>
                    ) : (
                        pipelines.map((item: any, index: number) => {
                                return (
                                    <Grid xs={12} sm={6} xl={4} key={index}
                                          sx={{height: 'auto', minHeight: '200px'}}>
                                        <Card
                                            sx={{height: '100%', display: 'flex', flexDirection: 'column'}}
                                        >
                                            <CardContent sx={{flexGrow: 1}}>
                                                <Typography gutterBottom variant="h5" component="h2">
                                                    {item.name}
                                                </Typography>
                                                <Grid container spacing={1} sx={{mb: 2}}>
                                                    {item.tags ? item.tags.map((tag: any, index: number) => {
                                                        return (
                                                            <Grid key={`pipeline-tag-${index}`}>
                                                                <Tooltip title={tag.name}>
                                                                    <Chip
                                                                        className={"acronym-chip"}
                                                                        label={tag.acronym}
                                                                        style={
                                                                            Tags.filter((t) =>
                                                                                t.acronym === tag.acronym)[0].colors
                                                                        }
                                                                        variant="outlined"
                                                                        size={"small"}
                                                                    />
                                                                </Tooltip>
                                                            </Grid>
                                                        )
                                                    }) : ''}
                                                </Grid>
                                                <Typography>
                                                    {item.summary}
                                                </Typography>
                                            </CardContent>
                                            <CardActions sx={{p: 2}}>
                                                <Link
                                                    to={"/showcase/pipeline/" + item.id}
                                                    state={{back: searchParams.toString()}}
                                                >
                                                    <Button size={"small"} variant={"contained"}>View</Button>
                                                </Link>
                                            </CardActions>
                                        </Card>
                                    </Grid>
                                );
                            }
                        ))}
                </Grid>
            }
            {isReady && pipelines.length > 0 ?
                pipelinePagination() : <></>
            }
        </>
    );
}

export default ItemGrid;
