import React, {Component} from 'react';

export default class DialogueTurn extends Component {
    constructor(props) {
        super(props);
    }

    render() {

        let image_src = '';
        if (this.props.bot_turn === 0) {
            image_src = 'public/img/bot_blue.jpg';
        } else {
            image_src = 'public/img/bot_red.jpg'
        }

        let active_class = 'bot_active_turn';
        if (!this.props.active){
             active_class = 'bot_inactive_turn'
        }

        let display_next = 'is_not_last_turn';
        if (this.props.display_next){
            display_next = 'is_last_turn'
        }

        let display_decision0 = 'is_not_dialogue_end';
        if (this.props.display_decision0){
            display_decision0 = 'is_dialogue_end'
        }
        let display_decision1 = 'is_not_dialogue_end';
        if (this.props.display_decision1){
            display_decision1 = 'is_dialogue_end'
        }

        return (
            <div className={active_class + " row"}>
                <div className={'col-lg-9 bot' + this.props.bot_turn}>
                    <div className={'bot_img_div' + this.props.bot_turn}>
                        <img src={image_src} className={'bot_img' + this.props.bot_turn}/>
                    </div>
                    <div className={'bot_text_div' + this.props.bot_turn}>
                        <p className={'speaker-id' + this.props.bot_turn}>{"Entity: " + this.props.bot_turn}</p>
                        <p>{this.props.text}</p>
                    </div>
                </div>
                <div className={"col-lg-3 next_turn" }>
                    <button type="button" className={"btn btn-primary " + display_next} onClick={() => this.props.onChildCallback()}>Next Exchange</button>
                    <button type="button" className={"col-lg-6 btn btn-danger " + display_decision0} onClick={() => this.props.onChildDecideCallback(0)}>Decide 0</button>
                    <button type="button" className={"col-lg-6 btn btn-danger " + display_decision1} onClick={() => this.props.onChildDecideCallback(1)}>Decide 1</button>
                </div>
            </div>
        )
    }
}