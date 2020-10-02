import React, {Component} from 'react';
import ApiClient from "../api_client";
import EntityForm from "./EntityForm";
import FinalRatingForm from "./FinalRatingForm";

const defaultValue = 50;

export default class SingleAnnotationForm extends Component {
    constructor(props) {
        super(props);
        this.state = {
            entity0_annotation: {},
            entity1_annotation: {},
            decided0: false,
            decided1: false,
            rating_provided: false
        };

        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleCheckChange = this.handleCheckChange.bind(this);
        this.handleUserName = this.handleUserName.bind(this);
        this.handleUserNameFocus = this.handleUserNameFocus.bind(this);
        this.handleRatingSubmit = this.handleRatingSubmit.bind(this);
        this.sendData = this.sendData.bind(this);
    }

    sendData() {
        if (this.state.decided0 && this.state.decided1 && this.state.rating_provided) {
            const apiClient = new ApiClient();
            let decision_data = {};
            decision_data.entity0_annotation = this.state.entity0_annotation;
            decision_data.entity1_annotation = this.state.entity1_annotation;
            decision_data.random_number = this.props.random_code;
            decision_data.convo_id = this.props.dialogue_id;
            decision_data.start_time = this.props.start_time;
            decision_data.user_name = this.props.user_name;
            decision_data.package_id = this.props.package_id;
            apiClient.postDecisionForDialogue(decision_data);
            this.props.random_dialogue_callback();
            this.setState({decided0: false, decided1: false, rating_provided: false})
        }
    }

    handleSubmit(data) {
        if (data.entity_number === 0) {
            this.setState({entity0_annotation: data, decided0: true});
        } else {
            this.setState({entity1_annotation: data, decided1: true});
        }
        this.props.entity_decision_cb(data.entity_number);
    }

    handleRatingSubmit(data) {
        data.entity0_annotation.is_human = this.state.entity0_annotation.is_human;
        data.entity1_annotation.is_human = this.state.entity1_annotation.is_human;

        data.entity0_annotation.decision_turn = this.state.entity0_annotation.decision_turn;
        data.entity1_annotation.decision_turn = this.state.entity1_annotation.decision_turn;

        data.entity0_annotation.entity_number = this.state.entity0_annotation.entity_number;
        data.entity1_annotation.entity_number = this.state.entity1_annotation.entity_number;
        this.setState({
            entity0_annotation: data.entity0_annotation,
            entity1_annotation: data.entity1_annotation,
            rating_provided: true
        }, this.sendData);
        this.props.final_rating_cb(this.state.entity0_annotation.is_human, this.state.entity1_annotation.is_human)
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

        let submission_cls0 = 'submission_div';
        if (this.props.decision_show0) {
            submission_cls0 = ''
        }

        let submission_cls1 = 'submission_div';
        if (this.props.decision_show1) {
            submission_cls1 = ''
        }

        let submission_cls_rating = 'submission_div';
        if (this.props.show_final_rating) {
            submission_cls_rating = ''
        }

        if (this.props.show_final_rating) {
            return (
                <div>
                    <div className={'row'}>
                        <div className={'col-lg-6 ' + submission_cls0}>
                            <EntityForm
                                entity_number={0}
                                submissionCallback={this.handleSubmit}
                                current_turn={this.props.current_turn}
                                no_spot_the_bot={this.props.no_spot_the_bot}
                                segmented={this.props.segmented}
                            />
                        </div>
                        <div className={'col-lg-6 ' + submission_cls1}>
                            <EntityForm
                                entity_number={1}
                                submissionCallback={this.handleSubmit}
                                current_turn={this.props.current_turn}
                                no_spot_the_bot={this.props.no_spot_the_bot}
                                segmented={this.props.segmented}
                            />
                        </div>
                    </div>
                    <div className={'row'}>
                        <div className={'col-lg-12 ' + submission_cls_rating}>
                            <FinalRatingForm
                                submissionCallback={this.handleRatingSubmit}
                            />
                        </div>
                    </div>
                </div>

            );
        } else {
            return (<div>
                <div className={'row'}>
                    <div className={'col-lg-6 ' + submission_cls0}>
                        <EntityForm
                            entity_number={0}
                            submissionCallback={this.handleSubmit}
                            current_turn={this.props.current_turn}
                            no_spot_the_bot={this.props.no_spot_the_bot}
                            segmented={this.props.segmented}
                        />
                    </div>
                    <div className={'col-lg-6 ' + submission_cls1}>
                        <EntityForm
                            entity_number={1}
                            submissionCallback={this.handleSubmit}
                            current_turn={this.props.current_turn}
                            no_spot_the_bot={this.props.no_spot_the_bot}
                            segmented={this.props.segmented}
                        />
                    </div>
                </div>
            </div>)
        }
    }

}