import React, {Component} from 'react';
import Dialogue from "./Dialogue";
import SubmittedForm from "./RandomCode";
import SingleAnnotationForm from "./SingleAnnotationForm";
import {TextField} from "@material-ui/core";
import ApiClient from "../api_client";
import MaxPackages from "./MaxPackages";

const start_turn = 0;
const next_turns = 1;


export default class DialoguePackageContainer extends Component {
    constructor(props) {
        super(props);
        this.state = {
            package_id: this.props.pkg_id,
            package_idx: 0,
            package_done: false,
            package_list: [null],
            dialogue_id: null,
            initial_turn: this.props.start_turn,
            deciding0: this.props.deciding,
            deciding1: this.props.deciding,
            decided0: false,
            decided1: false,
            decision_turn0: -1,
            decision_turn1: -1,
            rating_provided: false,
            current_turn: this.props.start_turn,
            start_time: -1,
            current_dialogue_length: -1,
            random_code: -1,
            annotated_packages: 0,
            max_allowed_packages: 0,
            user_name: localStorage.getItem("user_name") ? localStorage.getItem("user_name") : ""
        };
        this.dialogueDivRef = React.createRef();
        this.dialogueIdList = React.createRef();

        this.handleDecision = this.handleDecision.bind(this);
        this.handleNext = this.handleNext.bind(this);
        this.handleKeyEvent = this.handleKeyEvent.bind(this);
        this.dialogue_loaded_callback = this.dialogue_loaded_callback.bind(this);
        this.handleSubmission = this.handleSubmission.bind(this);
        this.handleEntityDecision = this.handleEntityDecision.bind(this);
        this.handleUserName = this.handleUserName.bind(this);
        this.handleUserNameFocus = this.handleUserNameFocus.bind(this);
        this.handleFinalRating = this.handleFinalRating.bind(this);
        this.getPackageForId = this.getPackageForId.bind(this);

    }

    componentDidMount() {
        document.addEventListener("keyup", this.handleKeyEvent);
        this.getPackageForId();

    }

    getPackageForId() {
        const apiClient = new ApiClient();
        const min = 1000000000;
        const max = 9999999999;
        let random_number = Math.round(min + Math.random() * (max - min));

        apiClient.getPackageForID(this.state.package_id).then(res => {
            this.setState({
                package_list: res.data.pkg_list,
                dialogue_id: res.data.pkg_list[this.state.package_idx].convo_id,
                current_turn: res.data.pkg_list[this.state.package_idx].start_turn,
                random_code: random_number
            });
        });

        apiClient.getNumberOfPackagesForUser(this.state.user_name).then(res => {
            this.setState({
                annotated_packages: res.data.package_for_user,
                max_allowed_packages: res.data.max_package_per_user
            })
        })
    }

    handleKeyEvent(event) {
        if (event.key === 'ArrowDown' && !(this.state.decided0 && this.state.decided1) && !(this.state.deciding0 || this.state.deciding1)) {
            this.handleNext();
        }
    }

    dialogue_loaded_callback(start_time, current_dialogue_length, is_human0, is_human1) {
        if (this.state.current_turn === -1) {
            this.setState({
                current_dialogue_length: current_dialogue_length,
                start_time: start_time,
                current_turn: current_dialogue_length,
                is_human0: is_human0,
                is_human1: is_human1
            });
        } else {
            this.setState({
                current_dialogue_length: current_dialogue_length,
                start_time: start_time,
                is_human0: is_human0,
                is_human1: is_human1,
                // deciding0: true,
                // deciding1: true,
                // current_turn: 5
            });
        }
    }

    handleDecision(start_time, entity_number) {
        if (this.state.user_name === null || this.state.user_name === '') {
            alert('Please Enter a Valid User Name');
        } else {
            if (entity_number === 0) {
                this.setState({deciding0: true, start_time: start_time})
            } else {
                this.setState({deciding1: true, start_time: start_time})
            }
        }
    }

    handleNext() {
        if (this.state.user_name === null || this.state.user_name === '') {
            alert('Please Enter a Valid User Name');
        } else {
            if (this.state.current_turn < this.state.current_dialogue_length) {
                let new_turn = this.state.current_turn + next_turns;
                this.setState({current_turn: new_turn})
            }

        }
    }

    handleFinalRating(is_human0, is_human1) {
        this.setState({rating_provided: true, is_human0_pred: is_human0, is_human1_pred: is_human1})
    }

    handleSubmission() {
        let new_package_idx = this.state.package_idx + 1;
        if (this.state.package_list.length > new_package_idx) {
            this.setState({
                package_idx: new_package_idx,
                dialogue_id: this.state.package_list[new_package_idx].convo_id,
                current_turn: this.state.package_list[new_package_idx].start_turn,
                initial_turn: this.props.start_turn,
                deciding0: this.props.deciding,
                deciding1: this.props.deciding,
                decided0: false,
                decided1: false,
                decision_turn0: -1,
                decision_turn1: -1,
                rating_provided: false,
                start_time: -1,
                current_dialogue_length: -1,
            })
        } else {
            this.setState({
                package_done: true
            })
        }
    }

    handleEntityDecision(entity_number) {
        if (entity_number === 0) {
            this.setState({decided0: true, deciding0: false, decision_turn0: this.state.current_turn});
        } else {
            this.setState({decided1: true, deciding1: false, decision_turn1: this.state.current_turn});
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
        let formClass = '';
        if (!(this.state.decided0 && this.state.decided1 && this.state.rating_provided && this.state.package_done)) {
            formClass = 'submission_div'
        }
        if (this.state.annotated_packages < this.state.max_allowed_packages) {
            return (
                <div>
                    <div className={"row"}>
                        <div className="col-lg-3">
                            <TextField
                                label="Required Worker ID"
                                variant={'outlined'}
                                onFocus={this.handleUserNameFocus}
                                onBlur={this.handleUserName}
                                onChange={this.handleUserName}
                                value={this.state.user_name}
                            />
                        </div>
                        <div className="col-lg-3">
                            <TextField
                                label="Conversation Progress"
                                variant={'outlined'}
                                disabled={true}
                                value={(100 * this.state.current_turn / this.state.current_dialogue_length).toFixed(3) + '%'}
                            />
                        </div>
                        <div className="col-lg-3">
                            <TextField
                                label="Package Progress"
                                variant={'outlined'}
                                disabled={true}
                                value={this.state.package_idx + '/' + this.state.package_list.length}
                            />
                        </div>
                        <div className="col-lg-3">
                            <TextField
                                label="Annotated Packages"
                                variant={'outlined'}
                                disabled={true}
                                value={this.state.annotated_packages + '/' + this.state.max_allowed_packages}
                            />
                        </div>
                    </div>
                    <div id={'dialogue-content'} className={'row'} onKeyUp={this.handleKeyEvent}>
                        <div className={"col"}>
                            <Dialogue
                                dialogue_id={this.state.dialogue_id}
                                dialogue_domains={this.props.dialogue_domain}
                                decisionCallback={this.handleDecision}
                                deciding={this.state.deciding0 || this.state.deciding1}
                                dialogue_loaded_cb={this.dialogue_loaded_callback}
                                nextCallback={this.handleNext}
                                decided0={this.state.decided0}
                                decided1={this.state.decided1}
                                current_turn={this.state.current_turn}
                            />
                        </div>
                    </div>


                    <div className={'row'}>
                        <div className={"col"}>
                            <SingleAnnotationForm
                                dialogue_id={this.state.dialogue_id}
                                current_turn={this.state.current_turn}
                                start_time={this.state.start_time}
                                random_dialogue_callback={this.handleSubmission}
                                entity_decision_cb={this.handleEntityDecision}
                                final_rating_cb={this.handleFinalRating}
                                entity0_decided={this.state.decided0}
                                entity1_decided={this.state.decided1}
                                decision_show0={(this.state.deciding0 && !this.state.decided0) || (this.state.current_turn === this.state.current_dialogue_length && !this.state.decided0)}
                                decision_show1={(this.state.deciding1 && !this.state.decided1) || (this.state.current_turn === this.state.current_dialogue_length && !this.state.decided1)}
                                show_final_rating={this.state.decided0 && this.state.decided1 && !this.state.rating_provided}
                                user_name={this.state.user_name}
                                no_spot_the_bot={!(this.props.start_turn === -1)}
                                package_id={this.props.pkg_id}
                                random_code={this.state.random_code}
                                segmented={this.props.segmented}
                            />
                        </div>
                    </div>
                    <div className={'row ' + formClass}>
                        <div className={"col-lg-12"}>
                            <SubmittedForm
                                random_code={this.state.random_code}
                                render={formClass === ''}
                            />
                        </div>
                    </div>
                </div>
            )
        } else {
            return (
                <div className={'row'}>
                    <div className={"col-lg-12"}>
                        <MaxPackages
                            ann_pkgs={this.state.annotated_packages}
                            max_allowed={this.state.max_allowed_packages}
                        />
                    </div>
                </div>
            )
        }


    }
}
