import React from 'react';
import { HashRouter, Route, hashHistory } from 'react-router-dom';
import DialougeDomainFilter from "./components/DialougeDomainFilter";
import DialogueContainer from "./components/DialougeContainer";

// import more components
export default (
    <HashRouter history={hashHistory}>
     <div>
      <Route path='/random' component={DialougeDomainFilter} />
      <Route path='/rd' exact component={() => <DialogueContainer convo_id={window.convo_id}/>} />
     </div>
    </HashRouter>
);

// if(window.convo_id === 0 ||window.convo_id == undefined){
//     ReactDOM.render(<DialougeDomainFilter />, document.getElementById('content'));
// }else{
//     ReactDOM.render(<Instructions/>, document.getElementById('infobox-container'));
//     ReactDOM.render(<DialogueContainer convo_id={convo_id} />, document.getElementById('content'));
// }

