import os
import pathlib

import clip
import matplotlib.pyplot as plt
import torch
from PIL import Image
from sklearn.manifold import TSNE
from tqdm import tqdm
import json


class VectorSearchBuild:
    def __init__(
        self, base_path="../scrape/content/", sources=["ebay", "dba"]):
        self.base_path = base_path
        self.sources = sources

        self.data = self.get_all_products()
        features_images = self.encode_images()
        features_text = self.encode_text()
        self.features_image_tensor, self.labels_image_tensor = self.get_tensors(features_images)
        self.features_text_tensor, self.labels_text_tensor = self.get_tensors(features_text)

    def get_all_products(self):
        data = {}
        i = 0
        for source in self.sources:
            loc = self.base_path + source + "/"
            products = os.listdir(loc)

            for product in products:
                base = loc + product
                data_file_path = "data.json"
                image_paths = os.listdir(pathlib.Path(base, "images"))

                # load data with json
                with open(pathlib.Path(base, data_file_path)) as f:
                    data_json = json.load(f)

                data[i] = {
                    "source": source,
                    "product": product,
                    "data_file_path": str(pathlib.Path(base, data_file_path)),
                    "data_json" : data_json,
                    "image_paths": [
                        pathlib.Path(base, "images", i) for i in image_paths
                    ],
                }

                i += 1

        return data

    def encode_images(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, preprocess = clip.load("ViT-B/32", device=device)
        features = {}
        for j in tqdm(self.data.keys(), desc="Encoding Images"):
            images = []
            for i in self.data[j]["image_paths"]:
                try:
                    images.append(preprocess(Image.open(i)).unsqueeze(0).to(device))
                except:
                    print(f"error with {i}")
                    pass
            images = torch.cat(images)
            with torch.no_grad():
                tmp = model.encode_image(images)
                features[j] = tmp

        return features
    
    def encode_text(self, max_length=30):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, preprocess = clip.load("ViT-B/32", device=device)
        features = {}
        for j in tqdm(self.data.keys(), desc="Encoding Text"):
            
            data_json = self.data[j]["data_json"]
            # data_json = {k: v for k, v in data_json.items() if k != 'url'}
            # text = str(data_json).replace('{','').replace('}','')

            text = data_json['title']

            if len(text) > max_length:
                text = text[:max_length]

            tokens = clip.tokenize([text]).to(device)
            with torch.no_grad():
                features[j] = model.encode_text(tokens)

        return features

    def get_tensors(self, features):
        features_tensor = torch.cat(list(features.values()))
        labels = []
        for k, v in features.items():
            count = v.shape[0]
            labels += [k] * count

        labels = torch.tensor(labels, dtype=torch.long)

        return features_tensor, labels

    def save(self):
        # image
        torch.save(self.features_image_tensor, "vectors/features_image.pt")
        torch.save(self.labels_image_tensor, "vectors/labels_image.pt")

        # text
        torch.save(self.features_text_tensor, "vectors/features_text.pt")
        torch.save(self.labels_text_tensor, "vectors/labels_text.pt")
    
        torch.save(
            self.data,
            "vectors/data.pt",
        )

    def visualize_embeddings(self):
        fig, ax = plt.subplots(1, 2, figsize=(9, 6))
        # images
        tsne = TSNE(n_components=2, perplexity=min(len(self.features_image_tensor)-1, 50), n_iter=5000, verbose=0)
        tsne_results = tsne.fit_transform(self.features_image_tensor.cpu().numpy())

        ax[0].scatter(tsne_results[:, 0], tsne_results[:, 1], c=self.labels_image_tensor, s=1)

        # text
        tsne = TSNE(n_components=2, perplexity=min(len(self.features_text_tensor)-1, 50), n_iter=5000, verbose=0)
        tsne_results = tsne.fit_transform(self.features_text_tensor.cpu().numpy())

        ax[1].scatter(tsne_results[:, 0], tsne_results[:, 1], c=self.labels_text_tensor, s=1)

        # make the figure look nice
        ax[0].set_xticks([])
        ax[0].set_yticks([])
        ax[1].set_xticks([])
        ax[1].set_yticks([])
        ax[0].set_title("Image Embeddings")
        ax[1].set_title("Text Embeddings")

        fig.suptitle("t-SNE of Image and Text Embeddings (colored by product)")
        fig.tight_layout()

        plt.show()


# main Build
if __name__ == "__main__":
    v = VectorSearchBuild(sources=["dba", "ebay"])  # ebay
    v.visualize_embeddings()
    v.save()
