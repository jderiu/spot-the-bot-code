import React, {Component} from 'react';
import Button from "@material-ui/core/Button";
import Slider from "@material-ui/core/Slider";
import Typography from "@material-ui/core/Typography";
import Checkbox from "@material-ui/core/Checkbox";
import Input from "@material-ui/core/Input";
import ApiClient from "../api_client";
import {TextField} from "@material-ui/core";
import withStyles from "@material-ui/core/styles/withStyles";

const defaultValue = 50;

const StyledButton = withStyles({
    root: {
        margin: '0 15px 10px 0',
    },
    label: {
        textTransform: 'capitalize',
    }
})(Button);

export default class AnnotationForm extends Component {
    constructor(props) {
        super(props);
        this.state = {
            fluencyWinner: null,
            sensitivenessWinner: null,
            specificityWinner: null
        };

        this.handleSubmit = this.handleSubmit.bind(this);
    }


    handleSubmit() {
        const apiClient = new ApiClient();
        const min = 1000000000;
        const max = 9999999999;

        let random_number = Math.round(min + Math.random() * (max - min));
        let user_name = localStorage.getItem("user_name") ? localStorage.getItem("user_name") : ""

        if (this.state.fluencyWinner === null || this.state.sensitivenessWinner === null || this.state.specificityWinner === null) {
            alert('Please decide which entity performs better');
        } else if (user_name === "") {
            alert('Please Enter your AMT WorkerID');
        } else {
            let data = {};
            data.entity0_annotation = {};
            data.entity1_annotation = {};
            data.entity0_annotation.fluencyValue = this.state.fluencyWinner === 'entity0' || this.state.fluencyWinner === 'tie';
            data.entity1_annotation.fluencyValue = this.state.fluencyWinner === 'entity1' || this.state.fluencyWinner === 'tie';

            data.entity0_annotation.sensitivenessValue = this.state.sensitivenessWinner === 'entity0' || this.state.sensitivenessWinner === 'tie';
            data.entity1_annotation.sensitivenessValue = this.state.sensitivenessWinner === 'entity1' || this.state.sensitivenessWinner === 'tie';

            data.entity0_annotation.specificityValue = this.state.specificityWinner === 'entity0' || this.state.specificityWinner === 'tie';
            data.entity1_annotation.specificityValue = this.state.specificityWinner === 'entity1' || this.state.specificityWinner === 'tie';

            data.random_number = random_number;

            this.props.submissionCallback(data);
        }


    }

    render() {

        let variant_dict = {
            true: 'contained',
            false: 'outlined'
        };

        let selected_variant = 'contained';
        let unselected_variant = 'outlined';

        return (
            <div className="card">
                <div className="card-body">
                    <form onSubmit={this.handleSubmit}>
                        <div className="container">
                            <div className={"row"}>
                                <Typography variant="h6" className={'col'}>Who perfromed better in:</Typography>
                            </div>

                            <div className={"row"}>
                                <Typography variant="h6" className={'col-lg-2'}>Fluency:</Typography>
                                <StyledButton variant={variant_dict[this.state.fluencyWinner === 'entity0']}
                                              className={'col-lg-2'}
                                              onClick={() => this.setState({fluencyWinner: 'entity0'})}
                                >
                                    Entity 0</StyledButton>
                                <StyledButton variant={variant_dict[this.state.fluencyWinner === 'entity1']}
                                              className={'col-lg-2'}
                                              onClick={() => this.setState({fluencyWinner: 'entity1'})}
                                >
                                    Entity 1</StyledButton>
                                <StyledButton variant={variant_dict[this.state.fluencyWinner === 'tie']}
                                              className={'col-lg-2'}
                                              onClick={() => this.setState({fluencyWinner: 'tie'})}
                                >
                                    No Difference</StyledButton>
                            </div>

                            <div className={"row"}>
                                <Typography variant="h6" className={'col-lg-2'}>Sensibleness:</Typography>
                                <StyledButton variant={variant_dict[this.state.sensitivenessWinner === 'entity0']}
                                              className={'col-lg-2'}
                                              onClick={() => this.setState({sensitivenessWinner: 'entity0'})}
                                >
                                    Entity 0</StyledButton>
                                <StyledButton variant={variant_dict[this.state.sensitivenessWinner === 'entity1']}
                                              className={'col-lg-2'}
                                              onClick={() => this.setState({sensitivenessWinner: 'entity1'})}
                                >
                                    Entity 1</StyledButton>
                                <StyledButton variant={variant_dict[this.state.sensitivenessWinner === 'tie']}
                                              className={'col-lg-2'}
                                              onClick={() => this.setState({sensitivenessWinner: 'tie'})}
                                >
                                    No Difference</StyledButton>
                            </div>


                            <div className={"row"}>
                                <Typography variant="h6" className={'col-lg-2'}>Specificity:</Typography>
                                <StyledButton variant={variant_dict[this.state.specificityWinner === 'entity0']}
                                              className={'col-lg-2'}
                                              onClick={() => this.setState({specificityWinner: 'entity0'})}>
                                    Entity 0</StyledButton>
                                <StyledButton variant={variant_dict[this.state.specificityWinner === 'entity1']}
                                              className={'col-lg-2'}
                                              onClick={() => this.setState({specificityWinner: 'entity1'})}>
                                    Entity 1</StyledButton>
                                <StyledButton variant={variant_dict[this.state.specificityWinner === 'tie']}
                                              className={'col-lg-2'}
                                              onClick={() => this.setState({specificityWinner: 'tie'})}>
                                    No Difference</StyledButton>
                            </div>

                            <div className={"row"}>
                                <Button variant="contained" color="primary" onClick={this.handleSubmit}
                                        className={'col-lg-2'}>
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