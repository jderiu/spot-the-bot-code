import React, {Component} from 'react';
import ApiClient from '../api_client';

export default class Leaderboard extends Component {
    constructor(props) {
        super(props);
        this.state = {leaderboard: {}};
    }

    componentDidMount() {
        this.loadLeaderboard();
    }

    componentWillReceiveProps(nextProps) {
        this.loadLeaderboard();
    }

    loadLeaderboard() {
        const apiClient = new ApiClient(); // No API key required for this endpoint!

        apiClient.getLeaderboard().then(res => {
            this.setState({leaderboard: res.data});
        });
    }

    render() {
        let tables = [];
        let leaderboard = this.state.leaderboard;

        return (
            <React.Fragment key={'fragment-leaderboard'}>
                {this.renderLeaderboardTable(leaderboard)}
            </React.Fragment>
        );
    }

    renderLeaderboardTable(currentLeaderboard) {
        let filterededArrData = Object.entries(currentLeaderboard).filter(entry => entry[1].number_of_annotations >= 20);

        //filterededArrData = arrData.filter(entry => entry[1].number_of_annotations > 20);

        let tableBody = filterededArrData.map(e => {
            return (
                <tr key={e[1].user_name} className={'row_' + e[1].user_name}>
                    <td>{e[1].user_name}</td>
                    <td>{e[1].number_of_annotations}</td>
                    <td>{e[1].score.toFixed(4)}</td>
                    <td>{e[1].elo_score.toFixed(4)}</td>
                </tr>
            );
        });

        return (
            <table className="table" key={'table-lederboard'}>
                <thead className="thead-light" key={'header-leaderboard'}>
                <tr key={'headerRow-leaderboard'}>
                    <th>User Name</th>
                    <th>Number of Annotations</th>
                    <th>Score</th>
                    <th>ELO Score</th>
                </tr>
                </thead>
                <tbody>{tableBody}</tbody>
            </table>
        )
    }
}