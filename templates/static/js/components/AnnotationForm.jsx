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
            user_name: localStorage.getItem("user_name") ? localStorage.getItem("user_name") : "",
            defaultValue: 50,
            comment0: "",
            comment1: ""
        };

        this.fluencyValue0Ref = React.createRef();
        this.sensitivenessValue0Ref = React.createRef();
        this.infromativenessValue0Ref = React.createRef();
        this.fluencyValue1Ref = React.createRef();
        this.sensitivenessValue1Ref = React.createRef();
        this.infromativenessValue1Ref = React.createRef();

        this.comment0Ref = React.createRef();
        this.comment1Ref = React.createRef();

        this.checked0 = false;
        this.checked1 = false;
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleCheckChange = this.handleCheckChange.bind(this);
        this.handleUserName = this.handleUserName.bind(this);
        this.handleUserNameFocus = this.handleUserNameFocus.bind(this);
    }


    handleSubmit() {
        if (this.state.user_name === null || this.state.user_name === '') {
            alert('Please Enter a Valid User Name');
        } else {
            const apiClient = new ApiClient();
            const min = 1000000000;
            const max = 9999999999;

            let random_number = Math.round(min + Math.random()*(max - min));
            let data = {};
            data.fluencyValue0 = this.fluencyValue0Ref.current.textContent;
            data.sensitivenessValue0 = this.sensitivenessValue0Ref.current.textContent;
            data.infromativenessValue0 = this.infromativenessValue0Ref.current.textContent;
            data.fluencyValue1 = this.fluencyValue1Ref.current.textContent;
            data.sensitivenessValue1 = this.sensitivenessValue1Ref.current.textContent;
            data.infromativenessValue1 = this.infromativenessValue1Ref.current.textContent;

            data.comment0 = this.comment0Ref.current.value;
            data.comment1 = this.comment1Ref.current.value;
            data.random_number = random_number;

            data.ent0Check = this.checked0;
            data.ent1Check = this.checked1;
            data.start_time = this.props.start_time;
            data.decision_turn = this.props.current_turn + 1;
            data.user_name = this.state.user_name;
            data.convo_id = this.props.dialogue_id;

            apiClient.postDecisionForDialogue(data);
            this.props.random_dialogue_callback(random_number)
        }
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
                    <div className="container">
                        <div className={"row"}>
                            <Typography variant="h6" className={'col'}>Decision for
                                Dialogue: {this.props.dialogue_id}</Typography>
                            <TextField
                                className={'col-lg-2'}
                                label="Required User Name"
                                onFocus={this.handleUserNameFocus}
                                onBlur={this.handleUserName}
                                onChange={this.handleUserName}
                                value={this.state.user_name}
                            />
                        </div>
                    </div>

                    <form onSubmit={this.handleSubmit}>
                        <div className="container">
                            <div className={"row"}>
                                <Typography variant="h6" className={'col'}>Which Entities are Human?</Typography>
                            </div>
                            <div className="row">
                                <div className={"col"}>
                                    <div className="row">
                                        <Typography className={"col-lg-3"} variant="subtitle1">Entity 0:</Typography>
                                        <Checkbox
                                            id={"ent0checkbox"}
                                            value="primary"
                                            inputProps={{'aria-label': 'primary checkbox'}}
                                            className={"col-lg-2"}
                                            onChange={this.handleCheckChange}
                                            defaultChecked={this.state.defaultCheck}
                                        >
                                        </Checkbox>
                                    </div>
                                </div>
                                <div className={"col"}>
                                    <div className="row">
                                        <Typography className={"col-lg-3"} variant="subtitle1">Entity 1:</Typography>
                                        <Checkbox
                                            id={"ent1checkbox"}
                                            value="primary"
                                            inputProps={{'aria-label': 'primary checkbox'}}
                                            className={"col-lg-2"}
                                            onChange={this.handleCheckChange}
                                            defaultChecked={this.state.defaultCheck}
                                        >
                                        </Checkbox>
                                    </div>
                                </div>

                            </div>

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
                                            Specificity:
                                        </Typography>
                                        <Slider
                                            defaultValue={defaultValue}
                                            valueLabelDisplay="auto"
                                            min={0}
                                            max={100}
                                            className={"col-lg-6"}
                                            id={"informSlider0"}
                                            ref={this.infromativenessValue0Ref}
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
                                            Specificity:
                                        </Typography>
                                        <Slider
                                            defaultValue={defaultValue}
                                            valueLabelDisplay="auto"
                                            min={0}
                                            max={100}
                                            className={"col-lg-6"}
                                            id={"informSlider1"}
                                            ref={this.infromativenessValue1Ref}
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