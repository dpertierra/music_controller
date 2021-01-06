import React, { Component } from "react";
import {
  Grid,
  Typography,
  Card,
  IconButton,
  LinearProgress,
  Collapse,
} from "@material-ui/core";
import PlayArrowIcon from "@material-ui/icons/PlayArrow";
import SkipNextIcon from "@material-ui/icons/SkipNext";
import SkipPreviousIcon from "@material-ui/icons/SkipPrevious";
import PauseIcon from "@material-ui/icons/Pause";
import Alert from "@material-ui/lab/Alert";

export default class MusicPlayer extends Component {
  constructor(props) {
    super(props);
    this.state = {
      playPauseStatus: "",
      votes: 0,
    };
  }

  playPauseSong() {
    let res = "";
    const requestOptions = {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
    };
    if (this.props.is_playing) {
      fetch("/spotify/pause", requestOptions)
        .then((response) => response.json())
        .then((json) => this.setState({ playPauseStatus: json.status }));
    } else {
      fetch("/spotify/play", requestOptions)
        .then((response) => response.json())
        .then((json) => this.setState({ playPauseStatus: json.status }));
    }
  }

  skipSong() {
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    };

    fetch("/spotify/skip", requestOptions);
  }

  prevSong() {
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    };

    fetch("/spotify/prev", requestOptions);
  }

  render() {
    let songProgress = (this.props.time / this.props.duration) * 100;
    return (
      <Grid container spacing={-3} justify="center">
        <Card align="center" justify="center">
          <Grid container alignItems="center">
            <Grid item align="center" xs={4}>
              <img
                src={this.props.image_url}
                height="100%"
                width="100%"
                alt="Album cover"
              />
            </Grid>
            <Grid item align="center" xs={8}>
              <Typography component="h5" variant="h5">
                {this.props.title}
              </Typography>
              <Typography color="textSecondary" variant="h5">
                {this.props.artist}
              </Typography>
              <div>
                <IconButton onClick={() => this.prevSong()}>
                  <SkipPreviousIcon />
                  <small>
                    {this.props.votes_prev}/{this.props.votes_required}{" "}
                  </small>
                </IconButton>
                <IconButton onClick={() => this.playPauseSong()}>
                  {this.props.is_playing ? <PauseIcon /> : <PlayArrowIcon />}
                </IconButton>
                <IconButton onClick={() => this.skipSong()}>
                  <small>
                    {this.state.votes}/{this.props.votes_required}{" "}
                  </small>
                  <SkipNextIcon />
                </IconButton>

                <Collapse in={this.state.playPauseStatus !== ""}>
                  {this.state.errorMsg !== "" ? (
                    <Alert
                      severity="error"
                      onClose={() => {
                        this.setState({ playPauseStatus: "" });
                      }}
                    >
                      {this.state.playPauseStatus}
                    </Alert>
                  ) : (
                    this.setState({ playPauseStatus: "" })
                  )}
                </Collapse>
              </div>
            </Grid>
          </Grid>
          <LinearProgress variant="determinate" value={songProgress} />
        </Card>
      </Grid>
    );
  }
}
