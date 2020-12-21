import React, { Component } from "react";
import { render } from "react-dom";
import HomePage from "./HomePage";
import JoinRoomPage from "./JoinRoomPage";
import CreateRoomPage from "./CreateRoomPage";
import { BrowserRouter as Router,
         Switch,
         Route,
         Link,
         Redirect} from "react-router-dom";

export default class App extends Component{
    constructor(props) {
        super(props);
    }

    render() {
        return <Router>
            <Switch>
                <Route exact path='/'><p>This is the home page</p></Route>
                <Route path='/join' component={JoinRoomPage}/>
                <Route path='/create' component={CreateRoomPage}/>
            </Switch>
        </Router>
    }
}

const appDiv =  document.getElementById("app");
render(<App />, appDiv);

