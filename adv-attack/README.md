# Adversarial Attacks in Machine Learning — Workshop

**CAS AI/ML Security Workshop**

This workshop covers the theory and practice of adversarial attacks across image, text, and language-model domains, as well as defenses and privacy attacks. It consists of 9 hands-on coding exercises organized by topic.

---

## Setup

### Prerequisites

Python 3.9+ is required. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Start Jupyter

```bash
jupyter lab
# or
jupyter notebook
```

Open the notebooks in `notebooks/` to work through exercises, or `solutions/` to see completed implementations.

---

## External Dependencies

### Exercise 7 — Memorization Extraction

This exercise requires a pretrained language model `secret_model.pth` and the `infoseclab` library from:

> https://github.com/ethz-privsec/infoseclab

Setup steps:
```bash
git clone https://github.com/ethz-privsec/infoseclab.git
cp infoseclab/data/secret_model.pth data/secret_model.pth
```

The notebook will work in stub/illustration mode if the model is not available.

### Exercise 3 — Adaptive Attacks

The detector in this exercise is implemented as a heuristic high-frequency noise detector — **no external `.pth` file is required**. If you want to use the pretrained `detector.pth` from the infoseclab repo, the notebook notes where to swap it in.

---

## Exercise Overview

| # | Topic | Time | Key Concepts |
|---|-------|------|-------------|
| 01 | FGSM Attack | ~20 min | Fast Gradient Sign Method, epsilon sweeps |
| 02 | PGD Attack | ~25 min | Projected Gradient Descent, targeted vs untargeted |
| 03 | Adaptive Attacks | ~30 min | Detector evasion, EoT for randomized defenses |
| 04 | Text Adversarial | ~20 min | TextFooler, word-level substitutions |
| 05 | Prompt Injection | ~20 min | Direct/indirect injection, sanitization defenses |
| 06 | Data Poisoning | ~25 min | Backdoor triggers, label flipping, poison rate |
| 07 | Memorization Extraction | ~30 min | Greedy decoding, constrained search, exhaustive extraction |
| 08 | Membership Inference | ~25 min | Shadow model attack, confidence-based signals |
| 09 | Adversarial Training | ~30 min | Robust training loop, clean vs adversarial accuracy tradeoff |

---

## Exercise Descriptions

### 01 — FGSM Attack (`01_fgsm_attack.ipynb`)

Implement the Fast Gradient Sign Method (Goodfellow et al. 2014) against a pretrained ResNet18 on CIFAR-10. You will compute gradients of the cross-entropy loss with respect to the input image and apply a single-step perturbation. Evaluate adversarial accuracy at multiple epsilon values and visualize the attack.

### 02 — PGD Attack (`02_pgd_attack.ipynb`)

Build on FGSM by implementing the Projected Gradient Descent attack (Madry et al. 2017). A base `PGD` class is provided; you implement the targeted variant `PGD_Targeted` by flipping the loss sign. Compare FGSM, PGD-untargeted, and PGD-targeted on the same images.

### 03 — Adaptive Attacks (`03_adaptive_attacks.ipynb`)

Learn why non-adaptive attacks overestimate defense strength. Implement two adaptive attack variants: (A) a joint attack that simultaneously fools the classifier and evades a high-frequency noise detector; (B) an EoT attack that averages gradients over random preprocessing transformations.

### 04 — Text Adversarial Attacks (`04_text_adversarial.ipynb`)

Use the TextAttack library to run a TextFooler attack against a DistilBERT sentiment classifier. Craft adversarial examples that flip positive reviews to negative (and vice versa) by substituting semantically similar words.

### 05 — Prompt Injection (`05_prompt_injection.ipynb`)

Explore prompt injection vulnerabilities in instruction-following LLMs using a mock LLM simulator. Design three injection payloads (direct override, embedded instruction, delimiter confusion) and test a simple regex-based sanitization defense.

### 06 — Data Poisoning & Backdoors (`06_data_poisoning.ipynb`)

Implement a backdoor attack on an MNIST classifier. Insert a small trigger patch into a fraction of training images and relabel them to a target class. Evaluate: (1) clean accuracy is maintained, (2) attack success rate on triggered test images. Also observe label-flipping effects.

### 07 — Memorization Extraction (`07_memorization_extraction.ipynb`)

*Requires `secret_model.pth` from infoseclab.* Attack a character-level language model to extract a memorized secret (password) using three strategies: greedy generation, constrained greedy (digits only), and exhaustive loss minimization over all 5-digit combinations.

### 08 — Membership Inference (`08_membership_inference.ipynb`)

Implement the shadow model attack (Shokri et al. 2017). Train a shadow model on a held-out dataset, collect confidence vectors from training members and non-members, then train a logistic regression attack classifier. Evaluate its ability to infer membership on a separate target model.

### 09 — Adversarial Training (`09_adversarial_training.ipynb`)

Implement adversarial training (Madry et al.) in TensorFlow/Keras. Start with a standard MNIST model, implement FGSM using `tf.GradientTape`, then write a custom adversarial training loop that minimizes the average of clean and adversarial loss. Compare clean and robust accuracy before and after adversarial training.

---

## References

- Goodfellow et al. (2014). *Explaining and Harnessing Adversarial Examples.* [FGSM]
- Madry et al. (2017). *Towards Deep Learning Models Resistant to Adversarial Attacks.* [PGD]
- Carlini & Wagner (2017). *Towards Evaluating the Robustness of Neural Networks.* [C&W]
- Athalye et al. (2018). *Synthesizing Robust Adversarial Examples.* [EoT]
- Carlini et al. (2019). *On Evaluating Adversarial Robustness.*
- Jin et al. (2020). *Is BERT Really Robust? A Strong Baseline for NLP Attack.* [TextFooler]
- Zou et al. (2023). *Universal and Transferable Adversarial Attacks on Aligned Language Models.* [GCG]
- Carlini et al. (2021). *Extracting Training Data from Large Language Models.*
- Shokri et al. (2017). *Membership Inference Attacks Against Machine Learning Models.*
- Shafahi et al. (2018). *Poison Frogs! Targeted Clean-Label Poisoning Attacks.*
