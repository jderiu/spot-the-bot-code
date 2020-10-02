import axios from 'axios';

const DIALOGUE_SYSTEM_PATH = '/api/dialouge_systems';
const DIALOGUE_DOMAINS = '/api/dialouge_domains';
const RANDOM_DIALOGUE_PATH = '/api/random_dialogue';
const LIST_OF_DIALOGUES = '/api/list_of_dialogues';
const DIALOGUE_FOR_ID = '/api/get_dialogue_for_id';

const POST_DECISION = '/api/post_decision';
const LEADERBOARD_PATH = '/api/get_leaderboard';
const SCORE_FOR_USER_PATH = '/api/get_score_for_user';
const PACKAGE_PATH = '/api/get_package_for_id';
const PACKAGE_FOR_USER = '/api/get_number_of_packages_for_user';


export default class ApiClient {

    getDialogueSystems() {
        return axios.get(DIALOGUE_SYSTEM_PATH, {});
    }

    getDialogueDomains() {
        return axios.get(DIALOGUE_DOMAINS, {});
    }

    getRandomDialogue(_dialogue_domains) {
        return axios.get(RANDOM_DIALOGUE_PATH, {params: {dialogue_domains: _dialogue_domains}});
    }

    getListOfDialoguesForSystem(_dialogue_system) {
        return axios.get(LIST_OF_DIALOGUES, {params: {dialogue_system: _dialogue_system}});
    }

    getListOfDialoguesForDomain(_domain) {
        return axios.get(LIST_OF_DIALOGUES, {params: {domain: _domain}});
    }

    getDialogueForID(_dialogue_id) {
        return axios.get(DIALOGUE_FOR_ID, {params: {dialogue_id: _dialogue_id}});
    }

    postDecisionForDialogue(data){
        return axios.post(POST_DECISION, data)
    }

    getLeaderboard(){
        return axios.get(LEADERBOARD_PATH, {})
    }

    get_score_for_user(user_name){
        return axios.get(SCORE_FOR_USER_PATH, {params: {user_name: user_name}})
    }

    getPackageForID(_package_id){
        return axios.get(PACKAGE_PATH, {params: {package_id: _package_id}});
    }
    getNumberOfPackagesForUser(_user_name){
        return axios.get(PACKAGE_FOR_USER, {params: {user_name: _user_name}});
    }

}