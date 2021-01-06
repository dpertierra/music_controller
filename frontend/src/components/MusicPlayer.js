import React, { Component } from "react";
import {
  Grid,
  Typography,
  Card,
  IconButton,
  LinearProgress,
} from "@material-ui/core";
import PlayArrowIcon from "@material-ui/icons/PlayArrow";
import SkipNextIcon from "@material-ui/icons/SkipNext";
import PauseIcon from "@material-ui/icons/Pause";

export default class MusicPlayer extends Component {
  constructor(props) {
    super(props);
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
        .then((json) => console.log(json));
    } else {
      fetch("/spotify/play", requestOptions)
        .then((response) => response.json())
        .then((json) => console.log(json));
    }
  }

  skipSong() {
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    };

    fetch("/spotify/skip", requestOptions);
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
                <IconButton onClick={() => this.playPauseSong()}>
                  {this.props.is_playing ? <PauseIcon /> : <PlayArrowIcon />}
                </IconButton>
                <IconButton onClick={() => this.skipSong()}>
                  <SkipNextIcon />
                </IconButton>
              </div>
            </Grid>
          </Grid>
          <LinearProgress variant="determinate" value={songProgress} />
        </Card>
      </Grid>
    );
  }
}
