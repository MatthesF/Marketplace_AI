import pathlib

import clip
import matplotlib.pyplot as plt
import numpy as np
import torch
from matplotlib import gridspec
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity


class VectorSearchInfer:
    def __init__(self, base_loc="../scrape/content/"):
        self.load()
        self.base_loc = base_loc

    def load(self, path="vectors/"):
        # load
        self.all_features = torch.load(pathlib.PosixPath(path, "features.pt"))
        self.labels = torch.load(pathlib.Path(path, "labels.pt"))
        self.data = torch.load(pathlib.Path(path, "data.pt"), weights_only=False)

    def search(self, path_or_text, visualize=True):
        self.check_data_type(path_or_text)
        features = self.encode(path_or_text)
        sim_sorted = np.argsort(
            cosine_similarity(features, self.all_features)
        ).flatten()

        least_similar_products, most_similar_products = (
            self.extract_extremes_from_sim_sorted(
                sim_sorted, n=3, method="products", verbose=False
            )
        )
        prices = self.get_similar_prices(most_similar_products)
        if visualize:
            self.visualize_product_similarities(
                path_or_text, most_similar_products, least_similar_products
            )

    def check_data_type(self, path_or_text):
        self.data_type = (
            "image" if path_or_text.split(".")[-1] in ["jpg", "jpeg", "png"] else "text"
        )

    def encode(self, path_or_text):
        # check if path is image or text
        device = "cuda" if torch.cuda.is_available() else "cpu"  # TODO: switch to mps
        model, preprocess = clip.load("ViT-B/32", device=device)

        if self.data_type == "image":
            im = Image.open(path_or_text)
            im_processed = preprocess(im).unsqueeze(0).to(device)

            with torch.no_grad():
                features = model.encode_image(im_processed)

        elif self.data_type == "text":
            text = clip.tokenize([path_or_text]).to(device)
            with torch.no_grad():
                features = model.encode_text(text)

        return features

    # which products are most and least similar
    def extract_extremes_from_sim_sorted(
        self, sim_sorted, n=3, method="products", verbose=False
    ):
        if method == "products":
            most_similar_products = []
            least_similar_products = []

            for idx in sim_sorted:
                label = self.labels[idx]
                if verbose:
                    print(f"idx: {idx}, label: {label}")

                if len(least_similar_products) >= n:
                    break

                if label not in least_similar_products:
                    least_similar_products.append(label.item())

            for idx in sim_sorted[::-1]:
                label = self.labels[idx]
                if verbose:
                    print(f"idx: {idx}, label: {label}")

                if len(most_similar_products) >= n:
                    break

                if label not in most_similar_products:
                    most_similar_products.append(label.item())

            return least_similar_products, most_similar_products

        elif method == "images":
            most_similar_images = []
            least_similar_images = []

            for idx in sim_sorted:
                label = self.labels[idx]
                if verbose:
                    print(f"idx: {idx}, label: {label}")

                if len(least_similar_images) >= n:
                    break

                if idx not in least_similar_images:
                    least_similar_images.append(idx)

            for idx in sim_sorted[::-1]:
                label = self.labels[idx]
                if verbose:
                    print(f"idx: {idx}, label: {label}")

                if len(most_similar_images) >= n:
                    break

                if idx not in most_similar_images:
                    most_similar_images.append(idx)

            return least_similar_images, most_similar_images

    # get price of most similar product
    def get_similar_prices(self, most_similar_products):
        prices = []
        for i in most_similar_products:
            loc = pathlib.Path(self.base_loc, self.data[i]["source"])

            path_json = pathlib.Path(loc, self.data[i]["product"], "data.json")
            import json

            with open(path_json, "r") as f:
                data_json = json.load(f)

            print(data_json["price"])
            prices.append(data_json["price"])

        return prices

    # visualize
    def visualize_product_similarities(
        self, path_or_text, most_similar_products, least_similar_products
    ):
        # set up figure
        def setup_figure():
            fig = plt.figure(figsize=(10, 4))
            gs = gridspec.GridSpec(
                2, 4, width_ratios=[1, 1, 1, 1], height_ratios=[1, 1]
            )

            ax0 = plt.subplot(gs[:, 0])
            similar_axes = [plt.subplot(gs[0, i]) for i in range(1, 4)]
            dissimilar_axes = [plt.subplot(gs[1, i]) for i in range(1, 4)]

            # put a green dashed line around the similar axes
            for ax_group in [similar_axes, dissimilar_axes]:
                for ax in ax_group:
                    for spine in ax.spines.values():
                        spine.set_color("green" if ax_group == similar_axes else "red")
                        spine.set_linestyle("dashed")
                        spine.set_linewidth(2)

                    ax.set_xticks([])
                    ax.set_yticks([])
                ax_group[0].set_ylabel(
                    "Similar" if ax_group == similar_axes else "Dissimilar"
                )
                ax_group[0].set_xlabel(
                    "Most similar" if ax_group == similar_axes else "Most dissimilar"
                )

            ax0.set_xticks([])
            ax0.set_yticks([])

            # ax0.imshow(Image.open(path))
            if self.data_type == "image":
                ax0.set_title("Input Image")
            else:
                ax0.set_title("Input Text")
            return fig, ax0, similar_axes, dissimilar_axes

        fig, ax0, similar_axes, dissimilar_axes = setup_figure()
        # display the example image next to the 5 most similar images

        if self.data_type == "image":
            ax0.imshow(Image.open(path_or_text))
        else:
            text_wrapped = "\n".join(
                [path_or_text[i : i + 20] for i in range(0, len(path_or_text), 20)]
            )
            # ax0.text(0.5, 0.5, path_or_text, fontsize=12, ha='center')
            ax0.text(0.5, 0.5, text_wrapped, fontsize=12, ha="center")

        for i in range(len(most_similar_products)):
            similar_axes[i].imshow(
                Image.open(self.data[most_similar_products[i]]["image_paths"][0])
            )
            similar_axes[i].set_title(self.data[most_similar_products[i]]["product"])

        for i in range(len(least_similar_products)):
            dissimilar_axes[i].imshow(
                Image.open(self.data[least_similar_products[i]]["image_paths"][0])
            )
            dissimilar_axes[i].set_title(
                self.data[least_similar_products[i]]["product"]
            )

        plt.tight_layout()
        plt.show()


# main Infer
if __name__ == "__main__":
    v = VectorSearchInfer()
    paths = [
        "../assets/multi_product/Screenshot 2024-10-10 at 18.48.57.png",
        "../assets/trial_products/chair.png",
        "../assets/model_outputs/belkin_bluetooth_music_receiver/image_1.png",
    ]

    # there are two ways to search, either by image or by text
    v.search(paths[0], visualize=True)
    v.search("device for listening to music", visualize=True)
