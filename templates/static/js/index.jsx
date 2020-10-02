import React from 'react';
import ReactDOM from 'react-dom';
import DialougeDomainFilter from "./components/DialougeDomainFilter";
import DialogueContainer from "./components/DialougeContainer";
import DialoguePackageContainer from "./components/DialougePackageContainer";
import Instructions from "./components/Instructions";
import Leaderboard from "./components/Leaderboard";

if(window.convo_id === 0 ||window.convo_id == undefined){
    if(window.show_leaderboard && !window.full_convo){
        ReactDOM.render(<Leaderboard />, document.getElementById('content'));
    }else if(window.pkg_id){
        ReactDOM.render(<Instructions />, document.getElementById('infobox-container'));
        if(window.segmented === true){
            ReactDOM.render(<DialoguePackageContainer pkg_id={window.pkg_id} start_turn={0} deciding={true} segmented={true}/>, document.getElementById('content'));
        }else{
            ReactDOM.render(<DialoguePackageContainer pkg_id={window.pkg_id} start_turn={0} deciding={false} segmented={false}/>, document.getElementById('content'));
        }
    }else{
        ReactDOM.render(<Instructions/>, document.getElementById('infobox-container'));
        ReactDOM.render(<DialougeDomainFilter />, document.getElementById('content'));
    }
}else{
    if(window.full_convo){
        ReactDOM.render(<Instructions/>, document.getElementById('infobox-container'));
        ReactDOM.render(<DialogueContainer convo_id={convo_id} start_turn={-1}/>, document.getElementById('content'));
    }else{
        ReactDOM.render(<Instructions/>, document.getElementById('infobox-container'));
        ReactDOM.render(<DialogueContainer convo_id={convo_id} start_turn={0}/>, document.getElementById('content'));
    }


}

