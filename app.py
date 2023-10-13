# BEGIN CODE HERE
import numpy as np
from flask import Flask, request, jsonify, json
from flask_pymongo import PyMongo
from flask_cors import CORS
from pymongo import TEXT
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
# END CODE HERE

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/pspi"
CORS(app)
mongo = PyMongo(app)
mongo.db.products.create_index([("name", TEXT)])


@app.route("/search", methods=["GET"])
def search():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Missing parameter: name"}), 400

    products = mongo.db.products.find({"name": {"$regex": name, "$options": "i"}})

    products = sorted(products, key=lambda k: np.sum([
        isinstance(k["name"], str) and name.lower() in k["name"].lower(),
        isinstance(k["color"], str) and k["color"].lower() == name.lower(),
        isinstance(k["size"], str) and k["size"].lower() == name.lower()
    ]), reverse=True)

    results = []
    for product in products:
        result = {
            "id": str(product["_id"]),
            "name": product["name"],
            "production_year": product["production_year"],
            "price": product["price"],
            "color": product["color"],
            "size": product["size"]
        }
        results.append(result)

    return jsonify(results), 200


@app.route('/add-product', methods=['POST'])
def add_product():
    data = request.get_json()

    if data["color"] not in [color for color in range(1, 4)] \
            or data["size"] not in [size for size in range(1, 5)]:
        return jsonify({"error": "Invalid color or size value"}), 400

    product = mongo.db.products.find_one({"name": data["name"]})

    if not product:
        mongo.db.products.insert_one(data)
        res_message = "Product added successfully"
    else:
        mongo.db.products.update_one(
            {"name": data["name"]},
            {"$set": {
                "production_year": data["production_year"],
                "price": data["price"],
                "color": data["color"],
                "size": data["size"]
            }}
        )
        res_message = "Product updated successfully"

    return jsonify({"success": res_message}), 200


@app.route("/content-based-filtering", methods=["POST"])
def content_based_filtering():
    input_data = request.get_json()

    if input_data["color"] not in [color for color in range(1, 4)] \
            or input_data["size"] not in [size for size in range(1, 5)]:
        return jsonify({"error": "Invalid color or size value"}), 400

    input_product = [input_data["production_year"], input_data["price"], input_data["color"], input_data["size"]]

    database_products = list(mongo.db.products.find())

    feature_vectors = []

    for product in database_products:
        if product["name"] == input_data["name"]:
            continue
        fv = np.array([product["production_year"], product["price"], product["color"], product["size"]])
        feature_vectors.append(fv)

    similarities = []
    for fv in feature_vectors:
        if np.linalg.norm(input_product) == 0 or np.linalg.norm(fv) == 0:
            continue
        sim = np.dot(input_product, fv) / (np.linalg.norm(input_product) * np.linalg.norm(fv))
        similarities.append(sim)

    recommended_products = []
    for i, sim in enumerate(similarities):
        print(f'Product: {database_products[i]["name"]}, Similarity: {sim}')
        if 0.7 < sim < 1:
            recommended_products.append(database_products[i]["name"])

    return jsonify(recommended_products), 200


@app.route("/crawler", methods=["GET"])
def crawler():
    semester = request.args.get('semester', type=int)
    if not semester:
        return jsonify({"error": "Missing parameter: semester"}), 400

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get("https://qa.auth.gr/el/x/studyguide/600000438/current")

    exam = "exam" + str(semester)
    exam_element = driver.find_element(By.ID, exam)

    courses = []
    course_elements = exam_element.find_elements(By.TAG_NAME, 'a')
    for course_element in course_elements:
        courses.append(course_element.text)
    driver.quit()
    return json.dumps(courses, ensure_ascii=False), 200
