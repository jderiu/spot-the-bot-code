import React, {Component} from 'react';

export default class MaxPackages extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                <div className={'card'}>
                    <div className={'card-body'}>
                        <div className="container">
                            <h3>Sorry, you already have annotated the maximum nubmer of Packages: {this.props.ann_pkgs} / {this.props.max_allowed}</h3>
                        </div>
                    </div>
                </div>
            </div>
        )
    }

}