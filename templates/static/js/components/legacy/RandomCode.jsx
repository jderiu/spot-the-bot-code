import React, {Component} from 'react';
import Leaderboard from "./Leaderboard";
import ApiClient from '../api_client';

export default class SubmittedForm extends Component {
    constructor(props) {
        super(props);

        this.computeScore = this.computeScore.bind(this);
    }

    computeScore() {
        let score = 0;
        if (this.props.is_human0 === this.props.is_human0_pred) {
            score += 0.5;
        }
        if (this.props.is_human1 === this.props.is_human1_pred) {
            score += 0.5;
        }
        score -= 0.3 * (this.props.decision_turn0 / this.props.convo_len);
        score -= 0.3 * (this.props.decision_turn1 / this.props.convo_len);
        return score
    }

    render() {
        if(!this.props.render){
            return (
                <div></div>
            );
        }

        let score_color = '';
        let score = this.computeScore();
        if (score <= 0.5) {
            score_color = 'red_score';
        } else {
            score_color = 'green_score';
        }

        let show_tips = 'submission_div';
        if (this.props.final_score < 0.75 && this.props.turn_penalty < 0.2) {
            show_tips = ''
        }

        return (
            <div>
                <div className={'card'}>
                    <div className={'card-body'}>
                        <div className="container">
                            <h3>Thank You for your submission. Your code is: {this.props.random_code}</h3>
                        </div>
                        <div className="container">
                            <h3>Your Score for this Conversation: <span
                                className={score_color}> {score.toFixed(3)}</span>
                            </h3>
                        </div>
                        <div className={"container " + show_tips}>
                            <h3 className="text-danger">
                                Your Scores seem to be low. Try to open more turns, you only
                                open {(this.props.turn_penalty*100).toFixed(3)} percent of the turns, which is a bit low.
                            </h3>
                        </div>
                    </div>
                </div>
                <div className={'card'}>
                    <div className={'card-body'}>
                        <h3>Leaderboard</h3>
                        <Leaderboard/>
                    </div>
                </div>
            </div>
        )
    }

}