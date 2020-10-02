import React, {Component} from "react";
import Typography from "@material-ui/core/Typography";
import Button from "@material-ui/core/Button";

const defaultValue = 50;

export default class EntityForm extends Component {
    constructor(props) {
        super(props);
        this.state = {
            defaultValue: 50,
            comment0: "",
            comment1: "",
            bot_value: "none"
        };

        this.fluencyValueRef = React.createRef();
        this.sensitivenessValueRef = React.createRef();
        this.specificityValueRef = React.createRef();
        this.comment0Ref = React.createRef();
        this.checked0 = false;

        this.handleRadioChange = this.handleRadioChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);

        this.handleHumanButton = this.handleHumanButton.bind(this);
        this.handleBotButton = this.handleBotButton.bind(this);
        this.handleUnsureButton = this.handleUnsureButton.bind(this);
    }

    componentDidMount() {
        this.setState({bot_value: 'none'})
    }

    handleRadioChange(event, newValue) {
        this.setState({bot_value: newValue});
    }

    handleSubmit() {
        if (this.state.bot_value === 'none') {
            alert('Please Decide if the Entity is a Bot or Human');
        } else {
            let data = {};
            if(this.state.bot_value !== 'unsure'){
                data.is_human = this.state.bot_value === 'true';
            }else{
                data.is_human = null;
            }
            data.decision_turn = this.props.current_turn + 1;
            data.entity_number = this.props.entity_number;
            this.props.submissionCallback(data);
            this.setState({bot_value: 'none'})
        }


    }

    handleHumanButton() {
        this.setState({bot_value: 'true'})
    }

    handleBotButton() {
        this.setState({bot_value: 'false'})
    }

    handleUnsureButton() {
        this.setState({bot_value: 'unsure'})
    }

    render() {
        let submission_cls1 = 'submission_div';
        if (this.props.no_spot_the_bot) {
            submission_cls1 = ''
        }

        let human_variant = 'outlined';
        let bot_variant = 'outlined';
        let unsure_variant = 'outlined';
        if (this.state.bot_value === 'true') {
            human_variant = 'contained';
        } else if (this.state.bot_value === 'false') {
            bot_variant = 'contained';
        } else if (this.state.bot_value === 'unsure') {
            unsure_variant = 'contained';
        }

        if (this.props.segmented) {
            return (
                <div className="card">
                    <div className="card-body">
                        <form onSubmit={this.handleSubmit}>
                            <div className="container">
                                <div className={"row " + submission_cls1}>
                                    <div className={"col"}>
                                        <div className="row">
                                            <Typography variant="h6" className={'col'}>
                                                Is Entity {this.props.entity_number}</Typography>
                                        </div>

                                        <div className="row">
                                            <Button variant={human_variant}
                                                    className={'col-lg-4'}
                                                    onClick={this.handleHumanButton}>
                                                Human</Button>
                                            <Button variant={bot_variant}
                                                    className={'col-lg-4'}
                                                    onClick={this.handleBotButton}>
                                                Bot</Button>
                                            <Button variant={unsure_variant}
                                                    className={'col-lg-4'}
                                                    onClick={this.handleUnsureButton}
                                            >
                                                Unsure</Button>
                                        </div>
                                    </div>
                                </div>

                                <div className={'row'}>
                                    <Button variant="contained" color="primary" onClick={this.handleSubmit}
                                            className={'col-lg-3'}>
                                        Submit
                                    </Button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            );
        }else{
            return (
            <div className="card">
                <div className="card-body">
                    <form onSubmit={this.handleSubmit}>
                        <div className="container">
                            <div className={"row " + submission_cls1}>
                                <div className={"col"}>
                                    <div className="row">
                                        <Typography variant="h6" className={'col'}>
                                            Is Entity {this.props.entity_number}</Typography>
                                    </div>

                                    <div className="row">
                                        <Button variant={human_variant}
                                                className={'col-lg-4'}
                                                onClick={this.handleHumanButton}>
                                            Human</Button>
                                        <Button variant={bot_variant}
                                                className={'col-lg-4'}
                                                onClick={this.handleBotButton}>
                                            Bot</Button>
                                    </div>
                                </div>
                            </div>

                            <div className={'row'}>
                                <Button variant="contained" color="primary" onClick={this.handleSubmit}
                                        className={'col-lg-3'}>
                                    Submit
                                </Button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        );
        }

    }
}