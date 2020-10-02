import React, {Component} from 'react';
import Leaderboard from "./Leaderboard";
import ApiClient from '../api_client';

export default class SubmittedForm extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        if(!this.props.render){
            return (
                <div></div>
            );
        }

        return (
            <div>
                <div className={'card'}>
                    <div className={'card-body'}>
                        <div className="container">
                            <h3>Thank You for your submission. Your code is: {this.props.random_code}</h3>
                        </div>
                    </div>
                </div>
            </div>
        )
    }

}