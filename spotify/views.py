from django.shortcuts import render, redirect
from api.models import Room
from .credentials import SECRET, CLIENTID, REDIRECT_URI
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from requests import Request, post

from .models import Vote
from .util import *

secret = SECRET
client_id = CLIENTID
redirect_uri = REDIRECT_URI


class AuthURL(APIView):
    def get(self, request):
        scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'

        url = Request('GET', 'https://accounts.spotify.com/authorize', params={'scope': scope,
                                                                               'response_type': 'code',
                                                                               'redirect_uri': redirect_uri,
                                                                               'client_id': client_id}).prepare().url
        return Response({'url': url}, status=status.HTTP_200_OK)


def spotify_callback(request):
    code = request.GET.get('code')
    error = request.GET.get('error')

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': secret
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')

    if not request.session.exists(request.session.session_key):
        request.session.create()
    update_or_create_user_tokens(request.session.session_key, access_token, token_type, expires_in, refresh_token)

    return redirect('frontend:')


class IsAuthenticated(APIView):
    def get(self, request):
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)


class CurrentSong(APIView):
    def get(self, request):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        host = room.host
        response = get_current_song(host)

        if 'error' in response or 'item' not in response:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        item = response.get('item')
        duration = item.get('duration_ms')
        progress = response.get('progress_ms')
        album_cover = item.get('album').get('images')[0].get('url')
        is_playing = response.get('is_playing')
        song_id = item.get('id')

        artist_string = ""
        for i, artist in enumerate(item.get('artists')):
            if i > 0:
                artist_string += ", "
            artist_string += artist.get('name')
        votes = len(Vote.objects.filter(room=room, song_id=song_id, skip=True))
        votes_prev = len(Vote.objects.filter(room=room, song_id=song_id, skip=False))
        song = {
            'title': item.get('name'),
            'artist': artist_string,
            'duration': duration,
            'time': progress,
            'image_url': album_cover,
            'is_playing': is_playing,
            'votes': votes,
            'votes_prev': votes_prev,
            'votes_required': room.votes_to_skip,
            'id': song_id,
        }

        self.update_room_song(room, song_id)

        return Response(song, status=status.HTTP_200_OK)

    def update_room_song(self, room, song_id):
        current_song = room.current_song
        if current_song != song_id:
            room.current_song = song_id
            room.save(update_fields=['current_song'])
            Vote.objects.filter(room=room).delete()


class PauseSong(APIView):
    def put(self, response):
        room_code_str = self.request.session.get('room_code')
        room_code = Room.objects.filter(code=room_code_str)
        if room_code.exists():
            room = room_code[0]
            if self.request.session.session_key == room.host or room.guest_can_pause:
                pause_song(room.host)
                return Response({"status": ""}, status=status.HTTP_200_OK)
            return Response({"status": "Can not pause songs ask the host for permission"},
                            status=status.HTTP_403_FORBIDDEN)
        return Response({"status": "Room not found"}, status=status.HTTP_400_BAD_REQUEST)


class PlaySong(APIView):
    def put(self, response):
        room_code_str = self.request.session.get('room_code')
        room_code = Room.objects.filter(code=room_code_str)
        if room_code.exists():
            room = room_code[0]
            if self.request.session.session_key == room.host or room.guest_can_pause:
                play_song(room.host)
                return Response({"status": ""}, status=status.HTTP_200_OK)
        return Response({"status": "Can not resume songs ask the host for permission"},
                        status=status.HTTP_403_FORBIDDEN)


class SkipSong(APIView):
    def post(self, request):
        room_code_str = self.request.session.get('room_code')
        room_code = Room.objects.filter(code=room_code_str)
        if room_code.exists():
            room = room_code[0]
            votes = Vote.objects.filter(room=room, song_id=room.current_song, skip=True)
            votes_needed = room.votes_to_skip
            if self.request.session.session_key == room.host or len(votes) + 1 >= votes_needed:
                votes.delete()
                skip_song(room.host)
            else:
                vote = Vote(user=self.request.session.session_key, room=room, song_id=room.current_song, skip=True)
                vote.save()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)


class PrevSong(APIView):
    def post(self, request):
        room_code_str = self.request.session.get('room_code')
        room_code = Room.objects.filter(code=room_code_str)
        if room_code.exists():
            room = room_code[0]
            votes = Vote.objects.filter(room=room, song_id=room.current_song, skip=False)
            votes_needed = room.votes_to_skip
            if self.request.session.session_key == room.host or len(votes) + 1 >= votes_needed:
                votes.delete()
                prev_song(room.host)
            else:
                vote = Vote(user=self.request.session.session_key, room=room, song_id=room.current_song, skip=False)
                vote.save()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
