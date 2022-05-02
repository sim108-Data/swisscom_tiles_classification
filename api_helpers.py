# Librairies
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from datetime import datetime, timedelta
import pandas as pd 
import os
#Request function ( This code to query the API is inspired on the github provided by swisscom: https://github.com/swisscom/mip/blob/master/query_swisscom_heatmaps_api.py 
# and from https://github.com/spaenleh/swisscom_challenge/blob/main/heatmaps_api.py )

BASE_URL = "https://api.swisscom.com/layer/heatmaps/demo"
TOKEN_URL = "https://consent.swisscom.com/o/oauth2/token"
MAX_NB_TILES_REQUEST = 100
headers = {"scs-version": "2"} 

client_id = "ggFAKlurRY2T3jkhMTU48coReeYZhfgj"  # customer key in the Swisscom digital market place
client_secret = "ve1cte7LqN7s0BRR"  # customer secret in the Swisscom digital market place

# Fetch an access token
client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)
oauth.fetch_token(token_url=TOKEN_URL, client_id=client_id,
                  client_secret=client_secret)


def get_tiles_from_districts(district_id):
    
    """
    INPUT: district id where tiles ar requested
    OUTPUT: DataFrame with all the tiles and their bbox

    """
    
    dist_tiles_resp = oauth.get(BASE_URL+"/grids/districts/{0}".format(district_id),headers=headers)
    if dist_tiles_resp.ok :
        dist_tiles_json=dist_tiles_resp.json()
        tile_ids = [t for t in dist_tiles_json["tiles"]]
        return pd.json_normalize(tile_ids,sep="_")



def get_score_for_tiles(tiles_id,dates,district_nbr):
    
    """
    INPUT: tiles_id: represent the all the tiles id and polygon for all requiered tiles
           dates: represent the time range than we want to analyze
    OUTPUT: datasets with all tiles id ,polygons and score for the desired timedelta
    
    """
    
    file_name_scores = f'Data/scores_clean_{district_nbr}.pkl'
    if not os.path.exists(file_name_scores):
        request_df = tiles_id.copy()
        request_df['numrequ'] = request_df.index.map(lambda x: x//MAX_NB_TILES_REQUEST)
        results_hours = []
        for query_date in dates:
            results = []
            for group, df_req in request_df.groupby('numrequ'):
                tile_ids_to_request = df_req.tileId.tolist()
                url =(BASE_URL + "/heatmaps/dwell-density/hourly/{0}".format(query_date.strftime('%Y-%m-%dT%H:%M')))
                json_response =  oauth.get(url, headers=headers, params={"tiles": tile_ids_to_request}).json()
                if json_response.get("tiles"):
                    results += json_response['tiles']
            df = pd.json_normalize(results).rename(columns={'score': query_date}).set_index('tileId')
            results_hours.append(df)
        copied_coords_df = request_df.drop(columns=["numrequ"]).set_index('tileId')
        score_df = copied_coords_df.join(results_hours)
        
        # drop tiles if more than half the day are Nan and then fill NaN with 10
        # as "only results involving more than 20 SIM cards are shared"
        # https://digital.swisscom.com/products/heatmaps/faq
        
        scores_clean = score_df.dropna(thresh=12).fillna(10)
        
        scores_clean.to_pickle(file_name_scores)
    else:
        print(f'Loading tile scores for district nbr {district_nbr} from cached file')
        scores_clean = pd.read_pickle(file_name_scores)
    return scores_clean

