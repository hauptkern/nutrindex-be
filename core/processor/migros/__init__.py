from curl_cffi import requests
from lxml import etree
from ..classifier import NutriScore
import base64


class MigrosExtractor:

    def get_product_id(self, barcode: str) -> dict[str, bool] | str:
        """
        Fetches product ID using the provided barcode.
        """
        url = f"https://rest.migros.com.tr/sanalmarket/products/barcode/{barcode}"

        try:
            # Send GET request with Chrome impersonation
            response = requests.get(url, impersonate="chrome")
            if response.status_code != 200:
                print(f"Error fetching product ID: HTTP {response.status_code}")
                print("Product ID not found.")

            # Parse XML response
            root = etree.fromstring(response.content)
            product_id = root.findtext(".//id")
            if product_id is None:
                print("Product ID not found.")
                return {"success": False}
            return product_id
        except Exception as e:
            print(f"Error fetching product.")
            return {"success": False}

    def get_product_info(self, product_id: str) -> dict:
        """
        Fetches product information including ingredients and nutritional values.
        """
        url = f"https://rest.migros.com.tr/sanalmarket/products/{product_id}"

        try:
            # Send GET request with Chrome impersonation
            response = requests.get(url, impersonate="chrome")
            if response.status_code != 200:
                return {"success": False}

            # Parse XML response
            root = etree.fromstring(response.content)
            # Check for success tag
            success_tag = root.find("successful")
            if success_tag is None or success_tag.text.lower() != "true":
                return {"success": False}

            # Extract product details
            product_details = self.extract_product_details(root)

            return {
                "success": True,
                **product_details
            }

        except Exception as e:
            raise e
            print(f"Error fetching product info: {e}")
            return {"success": False}

    def calculate_nutriscore(self, nutritional_values: dict) -> str:
        return NutriScore().calculate_nutri_score(
            energy_kcal=nutritional_values['calories'],
            sugars_g=nutritional_values["sugar"],
            saturated_fat_g=nutritional_values["saturated_fat"],
            sodium_mg=nutritional_values["salt"] * 100,
            fruits_veg_nuts_percent=0,
            fiber_g=nutritional_values.get('fibre', 0),
            protein_g=nutritional_values["protein"]
        )

    def extract_product_details(self, root: etree.Element) -> dict:
        """
        Extracts product details, ingredients, and nutritional values from the XML response.
        """
        product_name = self.extract_product_name(root)
        ingredients = self.extract_ingredients(root)
        nutritional_value = self.extract_nutritional_values(root)
        nutri_score = self.calculate_nutriscore(nutritional_value)
        img = self.extract_image(root)

        return {
            "product_name": product_name,
            "ingredients": ingredients,
            "nutritional_values": nutritional_value,
            "nutri_score": nutri_score,
            "img": img
        }

    def extract_image(self, root: etree.Element) -> str | None:
        img_url = root.findtext(".//PRODUCT_DETAIL")
        response = requests.get(img_url, impersonate="chrome")
        if response.status_code == 200 or response.status_code == 304:
            return base64.b64encode(response.content)
        return None

    def extract_product_name(self, root: etree.Element) -> str:
        """
        Extracts ingredients from the product description in the XML.
        """
        description = root.findtext(".//name")
        if description:
            return description
        return None

    def extract_ingredients(self, root: etree.Element) -> str:
        """
        Extracts ingredients from the product description in the XML.
        """
        description = root.findtext(".//description")
        if description:
            # Clean HTML tags from the description
            return self.parse_ingredients_from_description(description)
        return None

    def parse_ingredients_from_description(self, description_html: str) -> str:
        """
        Parses ingredients from the HTML description.
        """
        tree = etree.HTML(description_html)
        ingredients = tree.xpath("//strong[text()='İçindekiler']/following-sibling::text()")
        return ''.join(ingredients).strip() if ingredients else None

    def extract_nutritional_values(self, root: etree.Element) -> dict:
        """
        Extracts nutritional values from the XML if available.
        """
        nutritional_value = {}
        nutritional_elements = root.findall(".//NUTRITIONAL")

        for element in nutritional_elements:
            name = element.findtext("name")
            value = element.findtext("value")
            if name and value:
                # Convert name to a more standardized format
                name = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
                # Try to convert value to float, if not possible, keep it as string
                try:
                    value = float(value)
                except ValueError:
                    pass
                nutritional_value[name] = value

        # Ensure we have the most common nutritional values
        common_nutrients = {
            "enerji_kcal": "calories",
            "enerji_kj": "joules",
            "yağ_g": "fat",
            "doymuş_yağ_g": "saturated_fat",
            "trans_yağ_g": "trans_fat",
            "karbonhidrat_g": "carbohydrates",
            "şeker_g": "sugar",
            "protein_g": "protein",
            "lif_g": "fibre",
            "tuz_g": "salt"
        }

        result = {}
        for xml_key, result_key in common_nutrients.items():
            if xml_key in nutritional_value:
                result[result_key] = nutritional_value[xml_key]
        if "joules" in result:
            if result["joules"] < result["calories"]:
                proc = result["joules"]*4.184
                if result["calories"]-10 < proc < result["calories"]+10:
                    result["calories"] = result["joules"]
                    result.pop("joules")
        return result
