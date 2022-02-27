from api import Api

api = Api(verbose=True)


def download_lyrics(data, context):
    trigger_resource = context.resource
    print('--- Function triggered by change to: %s' % trigger_resource)

    path_parts = context.resource.split('/documents/')[1].split('/')
    collection_path = path_parts[0]
    document_path = '/'.join(path_parts[1:])
    track_id = document_path.split('/')[2]

    print("Collection path: ", collection_path)
    print("Document path: ", document_path)
    print("Track ID: ", track_id)

    print("Getting track from Spotify...")
    track = api.get_track(track_id)
    if track:
        print("Getting track from Genius...")
        genius = api.get_track_genius(track_id)
        if genius:
            lyrics = genius.get('lyrics', None)

            print("Posting track's lyrics on database...")
            api.post_track(track_id=track['id'], name=track['name'], lyrics=lyrics)
            print("--- Function successfully terminated!")
            return 201
        else:
            print("ATTENTION! Track not found on Genius!")
            return 404
    else:
        print("ATTENTION! Track not found on Spotify!")
        return 404
