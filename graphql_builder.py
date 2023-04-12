import streamlit as st
import requests
import datetime
import json

def create_graphql_query(original_product_type, selected_fields, time_range, filter_field,filter_value):
    query_template = '''
    query {query_name} {{
        product: {product_type}(
            limit: 10000,
            filter: {{
                tsRange: {{begin: "{start_time}T00:00:00", end: "{end_time}T23:59:59"}},
                {filter_clause}
            }},
            aggregate: {{count: ts}},
            groupBy: [{fields_group_by}],
            orderBy: [count_DESC]
        ) {{
            {fields}
        }}
    }}
    '''

    product_type_mapping = {
        "Real-time Events": "httpEvents",
        "Real-time Metrics": "httpMetrics"
    }

    query_name_mapping = {
        "Real-time Events": "EventsQuery",
        "Real-time Metrics": "MetricsQuery"
    }

    product_type = product_type_mapping[original_product_type]
    query_name = query_name_mapping[original_product_type]

    formatted_fields = "\n".join(selected_fields)
    fields_group_by = ",".join(selected_fields)

    start_time, end_time = time_range

    filter_clause = ''
    if filter_value.isnumeric():
        filter_clause = f'{filter_field}: {filter_value}'
    elif filter_field and filter_value:
        filter_clause = f'{filter_field}: \"{filter_value}\"'

    query = query_template.format(
        query_name=query_name,
        product_type=product_type,
        fields=formatted_fields,
        fields_group_by=fields_group_by,
        start_time=start_time,
        end_time=end_time,
        filter_clause=filter_clause,
    )

    return query





def execute_graphql_query(query, api_key, original_product_type):
    query_name_mapping = {
        "Real-time Events": "httpEvents",
        "Real-time Metrics": "httpMetrics"
    }

    query_name = query_name_mapping[original_product_type]

    if query_name == "httpEvents":
        graphql_url = 'https://api.azionapi.net/events/graphql'
    elif query_name == "httpMetrics":
        graphql_url = 'https://api.azionapi.net/metrics/graphql'
    else:
        raise ValueError("Tipo de produto inválido.")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Token {api_key}'
    }
    payload = {'query': query}

    response = requests.post(graphql_url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()['data']
    else:
        raise Exception(f"Erro na consulta GraphQL: {response.text}")



    
def process_and_display_data(data):
    if not data:
        st.error("Nenhum dado encontrado.")
        return

    product_type = list(data.keys())[0]
    st.write(f"Resultados para {product_type}:")

    json_data = json.dumps(data, indent=2)
    download_button = st.download_button(
        label="Baixar JSON",
        data=json_data,
        file_name="resultados.json",
        mime="application/json"
    )

    if download_button:
        st.success("Download iniciado!")

def main():
    st.sidebar.title("Configurações da API")
    api_key = st.sidebar.text_input("Insira sua chave de API:", value="", type="password")
    original_product_type = st.sidebar.selectbox("Selecione o tipo de produto", ["Real-time Events", "Real-time Metrics"])

    product_type_mapping = {
        "Real-time Events": "httpEvents",
        "Real-time Metrics": "httpMetrics"
    }

    filter_field = st.sidebar.text_input("Insira o campo de filtro desejado:")
    filter_value = st.sidebar.text_input("Insira o valor de filtro desejado:")

    product_type = product_type_mapping[original_product_type]

    if original_product_type == "Real-time Events":
        available_fields = [
            "ts", "source", "virtualhostId", "configurationId", "solutionId", "host",
            "requestTime", "requestMethod", "upstreamCacheStatus", "status",
            "proxyStatus", "upstreamStatus", "upstreamStatusStr", "upstreamBytesReceived",
            "scheme", "requestUri", "sessionid", "streamname", "sentHttpContentType",
            "serverProtocol", "requestLength", "bytesSent", "upstreamConnectTime",
            "upstreamHeaderTime", "upstreamResponseTime", "tcpinfoRtt", "remoteAddress",
            "remotePort", "naxsiAttackFamily", "naxsiAttackAction", "geolocCountryName",
            "geolocRegionName", "sslProtocol", "sslCipher", "sslSessionReused",
            "httpUserAgent", "httpReferer", "sentHttpXOriginalImageSize", "serverAddr",
            "upstreamAddr", "upstreamBytesSent", "wafLearning", "wafBlock",
            "wafTotalProcessed", "wafTotalBlocked", "wafScore", "wafMatch",
            "wafEvheaders", "requestId", "sslServerName", "stacktrace",
            "debugLog", "serverPort", "geolocAsn", "upstreamBytesReceivedStr",
            "upstreamConnectTimeStr", "upstreamHeaderTimeStr", "upstreamResponseTimeStr",
            "upstreamAddrStr", "upstreamBytesSentStr", "count", "sum", "max",
            "min", "avg"
        ]
    else:
        available_fields = [
            "configurationId", "host", "requestMethod", "upstreamCacheStatus",
            "status", "proxyStatus", "upstreamStatus", "scheme", "naxsiAttackFamily",
            "geolocCountryName", "geolocRegionName", "wafLearning", "wafBlock",
            "sourceLocPop", "remoteAddressClass", "requestTime",
            "upstreamBytesReceived", "requestLength", "bytesSent",
            "upstreamResponseTime", "requests", "dataTransferredIn", "dataTransferredOut",
            "dataTransferredTotal", "offload", "savedData", "missedData",
            "bandwidthTotal", "bandwidthSavedData", "bandwidthMissedData",
            "bandwidthOffload", "httpRequestsTotal", "httpsRequestsTotal",
            "edgeRequestsTotal", "edgeRequestsTotalPerSecond", "requestsOffloaded",
            "savedRequests", "missedRequests", "savedRequestsPerSecond",
            "missedRequestsPerSecond", "requestsPerSecondOffloaded",
            "requestsStatusCode2xx", "requestsStatusCode200", "requestsStatusCode204",
            "requestsStatusCode206", "requestsStatusCode3xx", "requestsStatusCode301",
            "requestsStatusCode302", "requestsStatusCode304", "requestsStatusCode4xx",
            "requestsStatusCode400", "requestsStatusCode403", "requestsStatusCode404",
            "requestsStatusCode5xx", "requestsStatusCode500", "requestsStatusCode502",
            "requestsStatusCode503", "requestsHttpMethodGet", "requestsHttpMethodPost",
            "requestsHttpMethodHead", "requestsHttpMethodOthers", "wafRequestsThreat",
            "wafRequestsBlocked", "wafRequestsAllowed", "wafRequestsXssAttacks",
            "wafRequestsRfiAttacks", "wafRequestsSqlAttacks", "wafRequestsOthersAttacks",
            "bandwidthImagesProcessedSavedData", "count", "sum", "max", "min", "avg"
]

    with st.container():
        st.write("Selecione os campos que deseja (limite de 20):")
        selected_fields = st.multiselect("Selecione os campos que deseja visualizar (limite de 20):", available_fields, default=[available_fields[0]])

    time_range = st.sidebar.date_input("Data de início e término", value=[datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()], min_value=datetime.date.today() - datetime.timedelta(days=60), max_value=datetime.date.today())

    if st.sidebar.button("Enviar"):
        if api_key == "":
            st.error("Por favor, insira sua chave de API.")
        else:
            query = create_graphql_query(original_product_type, selected_fields, time_range, filter_field, filter_value)
            data = execute_graphql_query(query, api_key, original_product_type)
            st.code(query)
            if data:
                json_data = json.dumps(data, indent=2)
                st.write("Download do resultado em JSON:")
                
                st.download_button("Baixar JSON", json_data, "result.json", "application/json")
            else:
                st.error("Nenhum dado encontrado.")



if __name__ == "__main__":
    main()
