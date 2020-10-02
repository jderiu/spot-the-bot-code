import React, {Component} from 'react';
import Button from "@material-ui/core/Button";
import Slider from "@material-ui/core/Slider";
import Typography from "@material-ui/core/Typography";
import Checkbox from "@material-ui/core/Checkbox";
import Input from "@material-ui/core/Input";
import ApiClient from "../api_client";
import {TextField} from "@material-ui/core";

const defaultValue = 50;

export default class AnnotationForm extends Component {
    constructor(props) {
        super(props);
        this.state = {
            defaultValue: 50,
            comment0: "",
            comment1: ""
        };

        this.fluencyValue0Ref = React.createRef();
        this.sensitivenessValue0Ref = React.createRef();
        this.specificityValue0Ref = React.createRef();

        this.fluencyValue1Ref = React.createRef();
        this.sensitivenessValue1Ref = React.createRef();
        this.specificityValue1Ref = React.createRef();

        this.comment0Ref = React.createRef();
        this.comment1Ref = React.createRef();

        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleCheckChange = this.handleCheckChange.bind(this);
        this.handleUserName = this.handleUserName.bind(this);
        this.handleUserNameFocus = this.handleUserNameFocus.bind(this);
    }


    handleSubmit() {
        const apiClient = new ApiClient();
        const min = 1000000000;
        const max = 9999999999;

        let random_number = Math.round(min + Math.random()*(max - min));
        let data = {};
        data.entity0_annotation = {};
        data.entity1_annotation = {};

        data.entity0_annotation.fluencyValue = this.fluencyValue0Ref.current.textContent;
        data.entity0_annotation.sensitivenessValue = this.sensitivenessValue0Ref.current.textContent;
        data.entity0_annotation.specificityValue = this.specificityValue0Ref.current.textContent;

        data.entity1_annotation.fluencyValue = this.fluencyValue1Ref.current.textContent;
        data.entity1_annotation.sensitivenessValue = this.sensitivenessValue1Ref.current.textContent;
        data.entity1_annotation.specificityValue = this.specificityValue1Ref.current.textContent;

        //data.entity0_annotation.comment0 = this.comment0Ref.current.value;
        //data.entity1_annotation.comment1 = this.comment1Ref.current.value;
        data.random_number = random_number;

        this.props.submissionCallback(data);

    }

    handleCheckChange(event, newValue) {
        let tid = event.target.id;
        if (tid === 'ent0checkbox') {
            this.checked0 = newValue;
        } else if (tid === 'ent1checkbox') {
            this.checked1 = newValue;
        }
    }

    handleUserName(event, newValue) {
        console.log("new value", event.target.value);
        this.setState({user_name: event.target.value});
        localStorage.setItem('user_name', this.state.user_name);
    }


    handleUserNameFocus() {
        this.setState({user_name: ""});
        localStorage.setItem('user_name', this.state.user_name);
    }


    render() {
        return (
            <div className="card">
                <div className="card-body">
                    <form onSubmit={this.handleSubmit}>
                        <div className="container">

                            <div className={'row'}>
                                <div className={"col-lg-6"}>
                                    <div className={"row"}>
                                        <Typography variant="h6" className={'col'}>How well does Entity 0
                                            perform?</Typography>
                                    </div>
                                    <div className={"row"}>
                                        <Typography gutterBottom className={"col-lg-4"}>
                                            Fluency:
                                        </Typography>
                                        <Slider
                                            defaultValue={defaultValue}
                                            valueLabelDisplay="auto"
                                            min={0}
                                            max={100}
                                            className={"col-lg-6"}
                                            id={"fluencySlider0"}
                                            ref={this.fluencyValue0Ref}
                                        />
                                    </div>
                                    <div className={"row"}>
                                        <Typography gutterBottom className={"col-lg-4"}>
                                            Sensibleness:
                                        </Typography>
                                        <Slider
                                            defaultValue={defaultValue}
                                            valueLabelDisplay="auto"
                                            min={0}
                                            max={100}
                                            className={"col-lg-6"}
                                            id={"senseSlider0"}
                                            ref={this.sensitivenessValue0Ref}
                                        />
                                    </div>
                                    <div className={"row"}>
                                        <Typography gutterBottom className={"col-lg-4"}>
                                            Specificity:
                                        </Typography>
                                        <Slider
                                            defaultValue={defaultValue}
                                            valueLabelDisplay="auto"
                                            min={0}
                                            max={100}
                                            className={"col-lg-6"}
                                            id={"informSlider0"}
                                            ref={this.specificityValue0Ref}
                                        />
                                    </div>

                                    <div className={"row"}>
                                        <Typography gutterBottom className={"col-lg-4"}>

                                        </Typography>
                                        <TextField
                                            defaultValue={''}
                                            className={'col-lg-6'}
                                            label="Optional Comments"
                                            multiline={true}
                                            variant={'outlined'}
                                            inputRef={this.comment0Ref}
                                            id={"comment0"}
                                        />
                                    </div>
                                </div>


                                <div className={"col-lg-6"}>
                                    <div className={"row"}>
                                        <Typography variant="h6" className={'col'}>How well does Entity 1
                                            perform?</Typography>
                                    </div>
                                    <div className={"row"}>
                                        <Typography gutterBottom className={"col-lg-4"}>
                                            Fluency:
                                        </Typography>
                                        <Slider
                                            defaultValue={defaultValue}
                                            valueLabelDisplay="auto"
                                            min={0}
                                            max={100}
                                            className={"col-lg-6"}
                                            id={"fluencySlider1"}
                                            ref={this.fluencyValue1Ref}
                                        />
                                    </div>
                                    <div className={"row"}>
                                        <Typography gutterBottom className={"col-lg-4"}>
                                            Sensibleness:
                                        </Typography>
                                        <Slider
                                            defaultValue={defaultValue}
                                            valueLabelDisplay="auto"
                                            min={0}
                                            max={100}
                                            className={"col-lg-6"}
                                            id={"senseSlider1"}
                                            ref={this.sensitivenessValue1Ref}
                                        />
                                    </div>
                                    <div className={"row"}>
                                        <Typography gutterBottom className={"col-lg-4"}>
                                            Specificity:
                                        </Typography>
                                        <Slider
                                            defaultValue={defaultValue}
                                            valueLabelDisplay="auto"
                                            min={0}
                                            max={100}
                                            className={"col-lg-6"}
                                            id={"informSlider1"}
                                            ref={this.specificityValue1Ref}
                                        />
                                    </div>
                                    <div className={"row"}>
                                        <Typography gutterBottom className={"col-lg-4"}>

                                        </Typography>
                                        <TextField
                                            defaultValue={''}
                                            className={'col-lg-6'}
                                            label="Optional Comments"
                                            multiline={true}
                                            variant={'outlined'}
                                            id={"comment1"}
                                            inputRef={this.comment1Ref}
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <Button variant="contained" color="primary" onClick={this.handleSubmit}>
                            Submit
                        </Button>
                    </form>
                </div>
            </div>
        );
    }

}