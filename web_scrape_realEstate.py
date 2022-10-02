import requests 
import json 
import pandas as pd 

# https://medium.com/@knappik.marco/python-web-scraping-how-to-scrape-the-api-of-a-real-estate-website-dc8136e56249

class RealtorScraper:
    def __init__(self, page_numbers):
        self.page_numbers = page_numbers
    
    def send_request(self, page_number, offset_parameter):

        url = "https://www.realtor.com/api/v1/hulk_main_srp?client_id=rdc-x&schema=vesta"
        headers = {"content-type": "application/json"}

        body = r'{"query":"\n\nquery ConsumerSearchMainQuery($query: HomeSearchCriteria!, $limit: Int, $offset: Int, $sort: [SearchAPISort], $sort_type: SearchSortType, $client_data: JSON, $bucket: SearchAPIBucket)\n{\n  home_search: home_search(query: $query,\n    sort: $sort,\n    limit: $limit,\n    offset: $offset,\n    sort_type: $sort_type,\n    client_data: $client_data,\n    bucket: $bucket,\n  ){\n    count\n    total\n    results {\n      property_id\n      list_price\n      primary_photo (https: true){\n        href\n      }\n      source {\n        id\n        agents{\n          office_name\n        }\n        type\n        spec_id\n        plan_id\n      }\n      community {\n        property_id\n        description {\n          name\n        }\n        advertisers{\n          office{\n            hours\n            phones {\n              type\n              number\n            }\n          }\n          builder {\n            fulfillment_id\n          }\n        }\n      }\n      products {\n        brand_name\n        products\n      }\n      listing_id\n      matterport\n      virtual_tours{\n        href\n        type\n      }\n      status\n      permalink\n      price_reduced_amount\n      other_listings{rdc {\n      listing_id\n      status\n      listing_key\n      primary\n    }}\n      description{\n        beds\n        baths\n        baths_full\n        baths_half\n        baths_1qtr\n        baths_3qtr\n        garage\n        stories\n        type\n        sub_type\n        lot_sqft\n        sqft\n        year_built\n        sold_price\n        sold_date\n        name\n      }\n      location{\n        street_view_url\n        address{\n          line\n          postal_code\n          state\n          state_code\n          city\n          coordinate {\n            lat\n            lon\n          }\n        }\n        county {\n          name\n          fips_code\n        }\n      }\n      tax_record {\n        public_record_id\n      }\n      lead_attributes {\n        show_contact_an_agent\n        opcity_lead_attributes {\n          cashback_enabled\n          flip_the_market_enabled\n        }\n        lead_type\n        ready_connect_mortgage {\n          show_contact_a_lender\n          show_veterans_united\n        }\n      }\n      open_houses {\n        start_date\n        end_date\n        description\n        methods\n        time_zone\n        dst\n      }\n      flags{\n        is_coming_soon\n        is_pending\n        is_foreclosure\n        is_contingent\n        is_new_construction\n        is_new_listing (days: 14)\n        is_price_reduced (days: 30)\n        is_plan\n        is_subdivision\n      }\n      list_date\n      last_update_date\n      coming_soon_date\n      photos(limit: 2, https: true){\n        href\n      }\n      tags\n      branding {\n        type\n        photo\n        name\n      }\n    }\n  }\n}","variables":{"query":{"status":["for_sale","ready_to_build"],"primary":true,"state_code":"NY"},"client_data":{"device_data":{"device_type":"web"},"user_data":{"last_view_timestamp":-1}},"limit":42,"offset":42,"zohoQuery":{"silo":"search_result_page","location":"New York","property_status":"for_sale","filters":{},"page_index":"2"},"sort_type":"relevant","geoSupportedSlug":"","bucket":{"sort":"modelF"},"by_prop_type":["home"]},"operationName":"ConsumerSearchMainQuery","callfrom":"SRP","nrQueryType":"MAIN_SRP","visitor_id":"ced33bb9-424a-4d02-ad61-5dda105f8569","isClient":true,"seoPayload":{"asPath":"/realestateandhomes-search/New-York/pg-2","pageType":{"silo":"search_result_page","status":"for_sale"},"county_needed_for_uniq":false}}'
        json_body = json.loads(body)

        json_body["variables"]["page_index"] = page_number
        json_body["seoPayload"] = page_number
        json_body["variables"]["offset"] = offset_parameter

        r = requests.post(url=url, json=json_body, headers=headers)
        json_data = r.json()
        return json_data
    
    def extract_features(self, entry):
        feature_dict = {
            "id": entry["property_id"],
            "price": entry["list_price"],
            "beds": entry["description"]["beds"],
            "baths": entry["description"]["baths"],
            "garage": entry["description"]["garage"],
            "stories": entry["description"]["stories"],
            "house_type": entry["description"]["type"],
            "lot_sqft": entry["description"]["lot_sqft"],
            "sqft": entry["description"]["sqft"],
            "year_built": entry["description"]["year_built"],
            "address": entry["location"]["address"]["line"],
            "postal_code": entry["location"]["address"]["postal_code"],
            "state": entry["location"]["address"]["state_code"],
            "city": entry["location"]["address"]["city"],
            "tags": entry["tags"]
        }
        
        if entry["location"]["address"]["coordinate"]:
            feature_dict.update({"lat": entry["location"]["address"]["coordinate"]["lat"]})
            feature_dict.update({"lon": entry["location"]["address"]["coordinate"]["lon"]})
            
        if entry["location"]["county"]:
            feature_dict.update({"county": entry["location"]["county"]["name"]})
        
        return feature_dict
    
    def parse_json_data(self):
        offset_parameter = 42
        
        feature_dict_list = []
        
        for i in range(1, self.page_numbers):
            json_data = self.send_request(page_number=i, offset_parameter=offset_parameter)
            offset_parameter += 42
            
            for entry in json_data["data"]["home_search"]["results"]:
                feature_dict = self.extract_features(entry)
                feature_dict_list.append(feature_dict)
                
        return feature_dict_list
    
    def create_dataframe(self):
        feature_dict_list = self.parse_json_data()
        
        df = pd.DataFrame(feature_dict_list)
        df.to_csv (r'/home/vivek27/vivek27/web_scrapper/code/csv_file/web2.csv', index = False)
        dummy_df = pd.get_dummies(df['tags'].explode()).groupby(level=0).sum()
        merged_df = pd.merge(df, dummy_df, left_index=True, right_index=True)
        # print(f'{dummy_df}\n\n and \n {merged_df}')
        return merged_df
    

if __name__ == "__main__":
    r = RealtorScraper(page_numbers=2)
    df = r.create_dataframe()