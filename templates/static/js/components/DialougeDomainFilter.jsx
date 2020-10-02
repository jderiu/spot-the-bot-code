import React, {Component} from 'react';
import ApiClient from '../api_client';
import DialogueList from "./DialougeList";

export default class DialougeSystemFilter extends Component {
    constructor(props) {
        super(props);
        this.state = {
            dialogue_domains: [], dialogue_domain_value: null
        };
        this.handleChange = this.handleChange.bind(this);
    }

    componentDidMount() {
        this.loadDialogueDomains();
    }

    loadDialogueDomains() {
        const apiClient = new ApiClient();

        apiClient.getDialogueDomains().then(res => {
            this.setState({dialogue_domains: res.data});
        });
    }

    handleChange(event) {
        this.setState({dialogue_domain_value: event.target.value});
    }

    render() {
        let dialogue_systems = this.state.dialogue_domains;

        let options = dialogue_systems.map((data) =>
            <option
                key={data.id}
                value={data.id}
            >
                {data.name}
            </option>
        );

        return (
            <div className={'col-lg-12'}>
                <div className={'row'}>
                    <select name="customSearch" className="custom-search-select" onChange={this.handleChange}>
                        <option key={null} value={null}>All Domains</option>
                        {options}
                    </select>
                </div>
                <div>
                    <DialogueList dialogue_domain={this.state.dialogue_domain_value}/>
                </div>
            </div>


        )
    }
}
