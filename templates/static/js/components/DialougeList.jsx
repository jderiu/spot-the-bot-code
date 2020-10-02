import React, {Component} from 'react';
import ApiClient from '../api_client';
import Dialogue from "./Dialogue";
import SingleAnnotationForm from "./SingleAnnotationForm";
import {TextField} from "@material-ui/core";

const start_turn = 0;
const next_turns = 1;

export default class DialogueList extends Component {
    constructor(props) {
        super(props);
        this.state = {
            dialogue_ids: [],
            value: null,
            initial_turn: start_turn,
            deciding0: false,
            deciding1: false,
            decided0: false,
            decided1: false,
            rating_provided: false,
            current_turn: start_turn,
            start_time: -1,
            current_dialogue_length: -1,
            user_name: localStorage.getItem("user_name") ? localStorage.getItem("user_name") : ""
        };
        this.dialogueDivRef = React.createRef();
        this.dialogueIdList = React.createRef();

        this.handleChange = this.handleChange.bind(this);
        this.handleDecision = this.handleDecision.bind(this);
        this.handleNext = this.handleNext.bind(this);
        this.handleKeyEvent = this.handleKeyEvent.bind(this);
        this.handleRandomDialogue = this.handleRandomDialogue.bind(this);
        this.dialogue_loaded_callback = this.dialogue_loaded_callback.bind(this);
        this.handleEntityDecision = this.handleEntityDecision.bind(this);
        this.handleFinalRating = this.handleFinalRating.bind(this);

        this.handleUserName = this.handleUserName.bind(this);
        this.handleUserNameFocus = this.handleUserNameFocus.bind(this);

    }

    componentDidMount() {
        this.loadListOfDialogues();
        document.addEventListener("keyup", this.handleKeyEvent);
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        if (this.props.dialogue_domain !== prevProps.dialogue_domain) {
            this.loadListOfDialogues();
            this.setState({value: null})
        }
    }

    loadListOfDialogues() {
        const apiClient = new ApiClient();

        apiClient.getListOfDialoguesForDomain(this.props.dialogue_domain).then(res => {
            this.setState({dialogue_ids: res.data});
        });
    }

    handleKeyEvent(event) {
        if (event.key === 'ArrowDown' && !(this.state.decided0 && this.state.decided1) && !(this.state.deciding0 || this.state.deciding1)) {
            this.handleNext();
        }
    }

    dialogue_loaded_callback(start_time, current_dialogue_length) {
        this.setState({current_dialogue_length: current_dialogue_length, start_time: start_time})
    }

    handleChange(event) {
        this.setState({value: event.target.value, decided: false, current_turn: start_turn});
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
            let new_turn = this.state.current_turn + next_turns;
            if(new_turn < this.state.current_dialogue_length){
                this.setState({current_turn: new_turn})
            }else{
                this.setState({
                    current_turn: new_turn,
                    deciding0: !this.state.decided0,
                    deciding1: !this.state.decided1
                })
            }

        }
    }

    handleRandomDialogue() {
        let new_value = this.state.dialogue_ids[Math.floor(Math.random() * this.state.dialogue_ids.length)];
        this.setState({
            value: new_value,
            decided0: false,
            decided1: false,
            deciding0: false,
            deciding1: false,
            rating_provided: false,
            current_turn: start_turn
        });
        this.dialogueIdList.current.value = new_value
    }

    handleFinalRating(){
        this.setState({rating_provided: true})
    }

    handleEntityDecision(entity_number) {
        if (entity_number === 0) {
            this.setState({decided0: true, deciding0: false});
        } else {
            this.setState({decided1: true, deciding1: false});
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
        let dialogue_ids = this.state.dialogue_ids;

        let formClass = '';
        if (!this.state.decided) {
            formClass = 'submission_div'
        }

        let options = dialogue_ids.map((data) =>
            <option
                key={data}
                value={data}
            >
                {data}
            </option>
        );

        if (!this.state.deciding0 && !this.state.deciding1 && !this.state.decided0 && !this.state.decided1) {
            return (
                <div>
                    <div className={'row'}>
                        <select id="dialogue-ids" className="custom-search-select col-lg-3" onChange={this.handleChange}
                                ref={this.dialogueIdList}>
                            <option key={null} value={null}>Select Item</option>
                            {options}
                        </select>
                        <button type="button" className={"btn btn-primary col-lg-2"}
                                onClick={this.handleRandomDialogue}>Load
                            Random Dialogue
                        </button>
                        <div className="col-lg-2 float-right">
                            <TextField
                                label="Required User Name"
                                onFocus={this.handleUserNameFocus}
                                onBlur={this.handleUserName}
                                onChange={this.handleUserName}
                                value={this.state.user_name}
                            />
                        </div>

                    </div>

                    <div id={'dialogue-content'} className={'row'} onKeyUp={this.handleKeyEvent}>
                        <div className={"col"}>
                            <Dialogue
                                dialogue_id={this.state.value}
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
                </div>
            )
        } else {
            return (
                <div>
                    <div className={'row'}>
                        <select id="dialogue-ids" className="custom-search-select" onChange={this.handleChange}
                                ref={this.dialogueIdList}>
                            <option key={null} value={null}>Select Item</option>
                            {options}
                        </select>
                        <button type="button" className={"btn btn-primary"} onClick={this.handleRandomDialogue}>Load
                            Random Dialogue
                        </button>
                        <div className="col-lg-2 float-right">
                            <TextField
                                label="Required User Name"
                                onFocus={this.handleUserNameFocus}
                                onBlur={this.handleUserName}
                                onChange={this.handleUserName}
                                value={this.state.user_name}
                            />
                        </div>
                    </div>

                    <div id={'dialogue-content'} className={'row'} onKeyUp={this.handleKeyEvent}>
                        <div className={"col"}>
                            <Dialogue
                                dialogue_id={this.state.value}
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
                                dialogue_id={this.state.value}
                                current_turn={this.state.current_turn}
                                start_time={this.state.start_time}
                                random_dialogue_callback={this.handleRandomDialogue}
                                entity_decision_cb={this.handleEntityDecision}
                                entity0_decided={this.state.decided0}
                                entity1_decided={this.state.decided1}
                                decision_show0={this.state.deciding0 && !this.state.decided0}
                                decision_show1={this.state.deciding1 && !this.state.decided1}
                                show_final_rating={this.state.decided0 && this.state.decided1 && !this.state.rating_provided}
                                user_name={this.state.user_name}
                                no_spot_the_bot={true}
                            />
                        </div>
                    </div>
                </div>
            )
        }


    }
}
