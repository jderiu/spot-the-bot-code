import React, {Component} from 'react';
import ApiClient from '../api_client';
import DialogueTurn from "./DialogueTurn";
import {animateScroll} from "react-scroll";

export default class Dialogue extends Component {
    constructor(props) {
        super(props);
        this.state = {
            current_dialogue: null,
            value: [],
            current_dialogue_length: -1

        };
        this.onChildNextClick = this.onChildNextClick.bind(this);
        this.onChildDecideClick = this.onChildDecideClick.bind(this);
    }

    scrollToBottom() {
        animateScroll.scrollToBottom({
            containedId: "content"
        });
    }

    componentDidMount() {
        if (this.props.dialogue_id !== null && this.props.dialogue_id !== undefined) {
            this.loadDialogueForID();
            this.setState({current_turn: 2}); //reset the to the first turns
        }
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        if (this.props.dialogue_id !== prevProps.dialogue_id || this.props.dialogue_domains !== prevProps.dialogue_domains) {
            if (this.props.dialogue_id !== null && this.props.dialogue_id !== undefined) {
                this.loadDialogueForID();
                this.setState({current_turn: 2}); //reset the to the first turns
            }
        }
        this.scrollToBottom();
    }

    loadDialogueForID() {
        const apiClient = new ApiClient();

        apiClient.getDialogueForID(this.props.dialogue_id).then(res => {
            let dialogue_len = res.data.convo.length;
            this.props.dialogue_loaded_cb(res.data.start_time, dialogue_len, res.data.is_human0, res.data.is_human1);
            this.setState({current_dialogue: res.data, current_dialogue_length: dialogue_len});
        });
    }

    loadRandomDialogue() {
        const apiClient = new ApiClient();

        apiClient.getRandomDialogue(this.props.dialogue_domains).then(res => {
            let dialogue_len = res.data.convo.length;
            this.setState({current_dialogue: res.data, current_dialogue_length: dialogue_len});
        });
    }

    onChildNextClick() {
        this.props.nextCallback(this.state.current_dialogue_length);
    }

    onChildDecideClick(entity_number) {
        this.props.decisionCallback(this.state.current_dialogue.start_time, entity_number);
    }

    //(key === current_dialogue.length - 1 && !this.props.decided0) ||
    //(key === current_dialogue.length - 1 && !this.props.decided1) ||
    render() {
        let current_dialogue = this.state.current_dialogue;

        if (this.state.current_dialogue != null) {
            let current_dialogue = this.state.current_dialogue.convo;
            console.log(current_dialogue.length);
            let turns = current_dialogue.map((item, key) =>
                <DialogueTurn ds_id={item.id}
                              text={item.text}
                              bot_turn={key % 2}
                              active={key <= this.props.current_turn}
                              display_next={this.props.current_turn === key && !(this.props.decided0 && this.props.decided1) && key < current_dialogue.length - 1 && !this.props.deciding}
                              display_decision0={(this.props.current_turn === key && !this.props.decided0 && !this.props.deciding)}
                              display_decision1={(this.props.current_turn === key && !this.props.decided1 && !this.props.deciding)}
                              onChildCallback={this.onChildNextClick}
                              onChildDecideCallback={this.onChildDecideClick}
                              key={'turn' + key}
                />
            );

            return (
                turns
            )
        } else
            return (
                <p>No Dialogue Loaded</p>
            )


    }

}