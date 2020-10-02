import React, {Component} from 'react';

export default class Home extends Component {
    constructor(props) {
        super(props);
        this.state = {
            show_instructions: true
        }
    }


    render() {
        let cls = '';
        if (!this.state.show_instructions) {
            cls = 'instruction-text-hidden'
        }

        return (
            <div>
                <div className={'row'}>
                    <h4 className={"col-lg-10"}>Instructions</h4>
                    <button type="button" className={"btn btn-primary col-lg-2"}
                            onClick={() => this.setState({show_instructions: !this.state.show_instructions})}>Show/Hide
                    </button>
                </div>
                <div className={'row'} id={cls}>
                    <p style={{margin: "0 0 10 0"}}>
                        Below you are shown a snipped of a conversation between two entities. Your task is to decide for each entitiy if it is a bot or a human.
                        Read each message carefully and then make your decision. In case you are not sure, select the "Unsure" option.
                    </p>
                    <p style={{margin: "0 0 5 0"}}>After your decision, rate the entities regarding the following features by selecting which entity performs better:</p>
                    <p style={{margin: "0 0 5 0"}}>
                        <strong>Fluency:</strong> Which entities' language is more fluent and grammatically correct?
                    </p>
                    <p style={{margin: "0 0 5 0"}}>
                        <strong>Specificity</strong>: Which entities' responses are more specific and explicit in the
                        given context? An answer is specific if it can be given only in the current context.
                        (If one says "I love tennis", and the other responds "That is nice!" or "What's your favorite
                        food?" then this is NOT specific. However, if the response is "I like Roger Federer!", it is
                        specific as it explicitly refers to the tennis context.)

                    </p>
                    <p style={{margin: "0 0 5 0"}}>
                        <strong>Sensible</strong>:Which entities' responses are more sensible? If the answer seems
                        confusing, illogical, contradictory, or factually wrong then it is NOT sensible.
                    </p>
                    <p>
                        After your decision click on the <strong>Submitt</strong> button. Then the next conversation in
                        the packet is loaded.
                        After you finished the last conversation in the batch, you will be prompted with a submission
                        code, which you have to paste in the mTurk form.
                    </p>
                </div>
            </div>
        )
    }
}
