# Setup
import os
import pathlib

import clip
import matplotlib.pyplot as plt
import torch
from PIL import Image
from sklearn.manifold import TSNE
from tqdm import tqdm


class VectorSearchBuild:
    def __init__(
        self, base_path="../scrape/content/", sources=["ebay", "dba"], datatype="image"
    ):
        self.base_path = base_path
        self.sources = sources
        self.data = self.get_all_products()
        self.image_features = self.encode_images()
        self.all_features, self.labels = self.get_tensors()

    def get_all_products(self):
        data = {}
        i = 0
        for source in self.sources:
            loc = self.base_path + source + "/"
            products = os.listdir(loc)

            for product in products:
                base = loc + product
                data_file_path = "/data.json"
                image_paths = os.listdir(pathlib.Path(base, "images"))

                data[i] = {
                    "product": product,
                    "data_file_path": base + data_file_path,
                    "source": source,
                    "image_paths": [
                        pathlib.Path(base, "images", i) for i in image_paths
                    ],
                }

                i += 1

        return data

    def encode_images(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, preprocess = clip.load("ViT-B/32", device=device)
        image_features = {}
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
                image_features[j] = tmp

        return image_features

    def get_tensors(self):
        all_features = torch.cat(list(self.image_features.values()))
        labels = []
        for k, v in self.image_features.items():
            count = v.shape[0]
            labels += [k] * count

        labels = torch.tensor(labels, dtype=torch.long)

        return all_features, labels

    def save_features(self):
        torch.save(self.all_features, "vectors/features.pt")
        torch.save(self.labels, "vectors/labels.pt")

    def save_data(self):
        torch.save(
            self.data,
            "vectors/data.pt",
        )

    def visualize_embeddings(self):
        # tsne
        tsne = TSNE(n_components=2, perplexity=50, n_iter=5000, verbose=0)
        tsne_results = tsne.fit_transform(self.all_features.cpu().numpy())

        fig, ax = plt.subplots(figsize=(7, 3))
        plt.title("t-SNE of Image Embeddings (colored by product)")
        scatter = ax.scatter(tsne_results[:, 0], tsne_results[:, 1], c=self.labels, s=1)
        plt.show()


# main Build
if __name__ == "__main__":
    v = VectorSearchBuild(sources=["dba", "ebay"])
    v.visualize_embeddings()
    v.save_features()
    v.save_data()
