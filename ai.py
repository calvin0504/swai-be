import google.generativeai as genai
from flask import Flask, jsonify,request
from pyngrok import ngrok
import requests
from flask_cors import CORS

app = Flask(__name__)



CORS(app)


NEWS_API_KEY = "c2e3fdf1f9b443caac124c58ee4cca5a"
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"


@app.route('/api/news', methods=['GET'])
def get_news():
    # 요청에서 파라미터 가져오기
    country = request.args.get('country', 'us')
    category = request.args.get('category', 'general')

    # NewsAPI 호출
    params = {
        'apiKey': NEWS_API_KEY,
        'country': country,
        'category': category
    }
    response = requests.get(NEWS_API_URL, params=params)


    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to fetch news', 'details': response.text}), response.status_code



@app.route('/api/recommend_stocks', methods=['POST'])
def recommend_stocks():
    data = request.get_json()
    news_title = data.get('news_title')

    if not news_title:
        return jsonify({'error': '뉴스 제목이 제공되지 않았습니다.'}), 400


    prompt = f"""
    뉴스 제목: "{news_title}"
    위 뉴스가 주식 시장에 미칠 영향을 분석하고, 관련이 있을 만한 주식 종목 3개를 추천해 주세요. 종목 티커와 이유를 함께 설명해 주세요.
    """
    try:
        response = model.generate_content(prompt)
        recommended_stocks = response.text

        return jsonify({'recommended_stocks': recommended_stocks})

    except Exception as e:
        return jsonify({'error': 'AI 요청 중 문제가 발생했습니다.', 'details': str(e)}), 500


@app.route('/api/get_tickers', methods=['POST'])
def get_tickers():
    try:
        data = request.get_json()
        news_title = data.get('news_title')

        if not news_title:
            return jsonify({'error': '뉴스 제목이 제공되지 않았습니다.'}), 400

        # 프롬프트 구성
        prompt = f"""
        뉴스 제목: "{news_title}"
        위 뉴스가 주식 시장에 미칠 영향을 분석하고, 관련성이 가장 높은 주식 종목 3개의 티커를 반환해 주세요.
        다른 정보는 제공하지 말고, 오직 티커만 쉼표로 구분하여 출력하세요.
        """

        # Generative AI 호출
        response = model.generate_content(prompt)

        # 응답 처리
        result_text = response.text.strip()
        tickers = [ticker.strip() for ticker in result_text.split(',') if ticker.strip()]

        if len(tickers) != 3:
            return jsonify({'error': '적절한 티커를 가져오지 못했습니다.', 'response': result_text}), 500

        return jsonify({'tickers': tickers})

    except Exception as e:
        return jsonify({'error': '예기치 못한 오류가 발생했습니다.', 'details': str(e)}), 500


@app.route('/api/hello', methods=['GET'])
def hello_world():
    return jsonify({'message': 'Hello, World!'})




if __name__ == '__main__':

    port = 5000


    public_url = ngrok.connect(port)
    print(f"Ngrok public URL: {public_url}")
    genai.configure(api_key='AIzaSyBu2soFWsLssyjZt5jbXpjH0xW885AKL8c')


    model = genai.GenerativeModel('gemini-pro')


    app.run(port=port)