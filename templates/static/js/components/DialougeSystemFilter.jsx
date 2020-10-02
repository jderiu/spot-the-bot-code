import React, {Component} from 'react';
import ApiClient from '../api_client';
import DialogueList from "./DialougeList";

export default class DialougeSystemFilter extends Component {
    constructor(props) {
        super(props);
        this.state = {
            dialogue_systems: [], dialogue_system_value: null};
        this.handleChange = this.handleChange.bind(this);
    }

    componentDidMount() {
        this.loadDialogueSystems();
    }

    loadDialogueSystems() {
        const apiClient = new ApiClient();

        apiClient.getDialogueSystems().then(res => {
            this.setState({dialogue_systems: res.data});
        });
    }

    handleChange(event) {
        this.setState({value: event.target.value});
    }

    render() {
        let dialogue_systems = this.state.dialogue_systems;

        let options = dialogue_systems.map((data) =>
            <option
                key={data.id}
                value={data.id}
            >
                {data.name}
            </option>
        );

        return (
            <div>
                <select name="customSearch" className="custom-search-select" onChange={this.handleChange}>
                    <option key={null} value={null}>Select Item</option>
                    {options}
                </select>
                <DialogueList dialogue_system={this.state.value}/>
            </div>

        )
    }
}
