# Topic Modeling on GitHub README Files Using Classical, Embedding-based and Hyperbolic Models
*(Mô hình hóa chủ đề trên tệp README GitHub bằng các mô hình cổ điển, nhúng và hyperbolic)*

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)
![GraphQL](https://img.shields.io/badge/GraphQL-Data_Collection-E10098?style=flat&logo=graphql)
![Transformers](https://img.shields.io/badge/Transformers-Embeddings-FFB000?style=flat&logo=huggingface)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-Classical_TM-F7931E?style=flat&logo=scikit-learn)
![LDA](https://img.shields.io/badge/LDA-Classical_Model-FF9E0F?style=flat)
![NMF](https://img.shields.io/badge/NMF-Classical_Model-FFA733?style=flat)
![BERTopic](https://img.shields.io/badge/BERTopic-Modern_TM-8A2BE2?style=flat)
![Top2Vec](https://img.shields.io/badge/Top2Vec-Modern_TM-9D50BB?style=flat)
![GTFomer](https://img.shields.io/badge/GTFomer-Hierarchical_TM-00C853?style=flat)



---

##  Research Objectives & Context *(Mục tiêu & Bối cảnh Nghiên cứu)*

* This research provides a systematic evaluation of five topic modeling approaches applied to a large-scale corpus of GitHub README files.
    *(Nghiên cứu này đánh giá có hệ thống năm phương pháp mô hình hóa chủ đề trên một kho ngữ liệu quy mô lớn gồm các tệp README trên GitHub)*
* `README.md` files are a critical source of unstructured text for mining insights, but their exponential growth and inconsistent user-generated tags pose significant challenges.
    *(Các tệp `README.md` là nguồn dữ liệu văn bản phi cấu trúc quan trọng để khám phá thông tin, nhưng sự phát triển theo cấp số nhân và tính không nhất quán của các thẻ (tags) do người dùng gán đã tạo ra thách thức đáng kể.)*

The primary objectives are: *(Mục tiêu chính của nghiên cứu là:)*

1.  To quantitatively **evaluate and compare** the performance of traditional and modern topic modeling methods in the context of technical software documentation.
    *(**Đánh giá và so sánh** định lượng hiệu suất của các phương pháp mô hình hóa chủ đề truyền thống và hiện đại trong ngữ cảnh tài liệu kỹ thuật phần mềm.)*
2.  To **introduce and assess** the effectiveness of **GTFomer**, a novel architecture designed for modeling hierarchical topic structures.
    *(**Giới thiệu và đánh giá** hiệu quả của **GTFomer**, một kiến trúc mới được thiết kế để mô hình hóa các chủ đề có cấu trúc phân cấp.)*
3.  To **provide empirical insights** into the thematic landscape of open-source projects on GitHub.
    *(**Cung cấp những hiểu biết thực nghiệm** về bối cảnh chủ đề của các dự án mã nguồn mở trên GitHub.)*

---

##  Dataset & Preprocessing *(Tập dữ liệu & Tiền xử lý)*

### Dataset *(Tập dữ liệu)*

* A meticulously constructed large-scale dataset of **57,368 unique `README.md` files** was collected via the GitHub GraphQL API.
    *(Một tập dữ liệu quy mô lớn được xây dựng tỉ mỉ gồm **57.368 tệp `README.md` duy nhất**, được thu thập thông qua GitHub GraphQL API.)*
* The collection strategy employed **multi-directional crawling** to ensure representation and minimize bias towards popular projects.
    *(Chiến lược thu thập dữ liệu được thiết kế đa chiều (multi-directional crawling) để đảm bảo tính đại diện và giảm thiểu sai lệch (bias) đối với các dự án phổ biến.)*
* For each of the 50 diverse tech topics, repositories were sampled evenly across four criteria: (1) most starred, (2) most forked, (3) most recently updated, and (4) best match.
    *(Đối với mỗi trong số 50 chủ đề công nghệ đa dạng, các kho lưu trữ được lấy mẫu đồng đều dựa trên bốn tiêu chí: (1) nhiều sao nhất, (2) được fork nhiều nhất, (3) được cập nhật gần đây nhất, và (4) phù hợp nhất.)*

### Preprocessing Strategy *(Chiến lược tiền xử lý)*

The pipeline was tailored for each model type:
*(Quá trình tiền xử lý được điều chỉnh riêng cho từng loại mô hình:)*

* **Classical Models (LDA, NMF):** Required rigorous preprocessing, including lowercasing, noise removal (URLs, code blocks, Markdown), stopword removal (with a custom list of tech terms like 'install', 'usage'), and lemmatization.
    *(**Mô hình cổ điển (LDA, NMF):** Cần tiền xử lý nghiêm ngặt bao gồm chuyển đổi chữ thường, loại bỏ nhiễu (URL, khối mã, cú pháp Markdown), loại bỏ từ dừng (bao gồm cả danh sách tùy chỉnh các thuật ngữ kỹ thuật như 'install', 'usage'), và rút gọn từ (lemmatization).)*
* **Embedding-based Models (BERTopic, Top2Vec, GTFormer):** Used raw or minimally processed text to preserve semantic context, fully leveraging the capabilities of Transformer models (e.g., `all-MiniLM-L6-v2`).
    *(**Mô hình dựa trên nhúng (BERTopic, Top2Vec, GTFormer):** Chỉ sử dụng văn bản thô hoặc được xử lý tối thiểu để bảo toàn ngữ cảnh ngữ nghĩa và cấu trúc cú pháp, tận dụng tối đa khả năng của các mô hình Transformer (ví dụ: `all-MiniLM-L6-v2`).)*

---

##  Topic Models Compared *(So sánh các Mô hình Chủ đề)*

Five models were compared, representing three generations of topic modeling:<br>
*(Năm mô hình được so sánh, đại diện cho ba thế hệ mô hình hóa chủ đề khác nhau:)*

| Model Type | Model | Base Methodology | Characteristics |
| :--- | :--- | :--- | :--- |
| **Classical** | **LDA** (Latent Dirichlet Allocation) | Probabilistic generative model assuming documents are mixtures of topics. | Ignores word semantics, requires manual $k$ (topic count) selection. |
| | **NMF** (Non-negative Matrix Factorization) | Linear algebra technique decomposing the TF-IDF matrix. | Often more stable than LDA on short-text corpora like READMEs. |
| **Modern (Embedding-based)** | **Top2Vec** | Jointly embeds documents and words in a semantic space, using UMAP & HDBSCAN. | Generates a flat list of topics; automatically determines $k$. |
| | **BERTopic** | Uses Transformer (BERT) embeddings, UMAP, HDBSCAN, and c-TF-IDF for keyword extraction. | Generates a flat list of topics. |
| **Proposed (Hierarchical)** | **GTFomer** (Graph–Transformer Topic Model) | Hybrid architecture integrating a **Hierarchical Graph Neural Network (HGNN)** and a Transformer encoder in **Hyperbolic Space** (Poincaré ball) to capture tree-like structures. | Aims to learn and preserve hierarchical structures. |

*(**Ghi chú về bảng:**)*
* *(**Cổ điển (Classical):** LDA, NMF)*
* *(**Hiện đại (Modern/Embedding-based):** Top2Vec, BERTopic)*
* *(**Đề xuất/Phân cấp (Proposed/Hierarchical):** GTFomer)*

---

##  Experimental Results & Discussion *(Kết quả Thực nghiệm & Thảo luận)*

Performance was evaluated using $C_v$ Coherence, Perplexity, Jensen–Shannon Divergence (JSD), and Topic Superiority Score.<br>
*(Hiệu suất được đánh giá bằng các tiêu chí như Độ mạch lạc ($C_v$), Perplexity (Độ phức tạp), Jensen–Shannon Divergence (JSD), và Topic Superiority Score.)*

#### Key Performance Comparison ($C_v$ Coherence Score) *(So sánh hiệu suất chính (Điểm Độ mạch lạc $C_v$):)*

| Model | Type | Topic Count ($k$) | Coherence ($C_v$) | Remarks |
| :--- | :--- | :--- | :--- | :--- |
| **BERTopic** | Modern | 20 | **0.72753** | Achieved the highest score, indicating semantically rich and distinct topics. |
| **NMF** | Classical | 20 | 0.71422 | Performed well with a moderate $k$, outperforming LDA. |
| **LDA** | Classical | 45 | 0.579 (peak) | Performance improved as $k$ increased (35–45), but Perplexity also rose, indicating a trade-off. |
| **Top2Vec** | Modern | 204 (auto-detected) | 0.37716 | Scored lowest due to a very high $k$, reflecting **topic fragmentation** and sensitivity to boilerplate text. |

Findings:

* BERTopic achieved the highest coherence (0.72753), confirming its strong ability to generate semantically meaningful clusters.
* NMF outperformed LDA, showing robust results on README data.
* LDA improved with larger $k$, though at the cost of increased perplexity.
* Top2Vec detected many small topics ($k=204$), but coherence dropped due to topic fragmentation from noisy boilerplate text.<br>
*(BERTopic đạt điểm mạch lạc cao nhất, NMF vượt LDA, trong khi Top2Vec gặp hiện tượng phân mảnh chủ đề. Kết quả cho thấy các mô hình hiện đại có ưu thế trong việc nắm bắt ngữ nghĩa so với mô hình xác suất cổ điển.)*

#### GTFomer Evaluation *(Đánh giá GTFomer)*

* GTFomer focused on modeling hierarchical structure rather than a flat set of topics.
    *(GTFomer tập trung vào việc mô hình hóa cấu trúc phân cấp thay vì tập hợp chủ đề phẳng.)*
* It used Latent Semantic Analysis (LSA) and hierarchical clustering to build a topic tree, which was then embedded in **Poincaré Space (Hyperbolic Space)**.
    *(Nó sử dụng Phân tích ngữ nghĩa tiềm ẩn (LSA) và gom cụm phân cấp để xây dựng cây chủ đề, sau đó nhúng nó vào **Không gian Poincaré (Hyperbolic Space)**.)*
* GTFomer was evaluated on a Level Prediction task, achieving a **best validation Perplexity of 0.3255**.
    *(GTFomer được đánh giá bằng tác vụ Level Prediction (Dự đoán cấp độ phân cấp). Mô hình đạt được **Perplexity xác thực tốt nhất là 0.3255**.)*
* While this perplexity is higher than in typical generative tasks, it indicates the model is **significantly better than random guessing** at capturing complex hierarchical structures, proving the efficacy of hyperbolic graph embeddings.
    *(Mặc dù Perplexity này cao hơn so với các tác vụ sinh thông thường, nó cho thấy mô hình **tốt hơn đáng kể so với đoán ngẫu nhiên** trong việc nắm bắt cấu trúc phân cấp phức tạp, chứng minh tính hiệu quả của việc nhúng đồ thị vào không gian hyperbolic.)*

---

##  Conclusion *(Kết luận)*

The empirical findings highlight a trade-off between models:
*(Các phát hiện thực nghiệm nhấn mạnh sự đánh đổi giữa các mô hình:)*

* **Classical models (LDA, NMF)**: Effective for well-defined, flat topics when finely tuned; NMF performs better on README data.
* **Embedding-based models (BERTopic, Top2Vec)**: BERTopic excels in semantic coherence, while Top2Vec struggles with noisy texts.
* **Hierarchical model (GTFomer)**: Introduces a novel direction by embedding hierarchical topic structures in hyperbolic space, offering improved interpretability for complex, multi-level software corpora.<br>
*(Nghiên cứu cho thấy sự đánh đổi rõ rệt giữa các phương pháp. Mô hình cổ điển hiệu quả với chủ đề phẳng; mô hình nhúng, đặc biệt là BERTopic, vượt trội về ngữ nghĩa; còn GTFomer mở ra hướng mới trong việc mô hình hóa cấu trúc chủ đề phân cấp phức tạp của dữ liệu phần mềm)*

---

##  Authors *(Nhóm Thực hiện)*

**Students:** *(Sinh viên thực hiện)*  
- Hồ Gia Thành  
- Huỳnh Thái Linh  
- Trương Minh Khoa  

**Supervisor:** *(Giảng viên hướng dẫn)* *ThS. Lê Nhật Tùng*  
**University:** *(Trường)* Trường Đại học Công nghệ TP. Hồ Chí Minh — *Khoa học Dữ liệu*  
**Year:** *(Năm thực hiện)* 2025

---

> © 2025 — Project: *Topic Modeling on GitHub README Files Using Classical, Embedding-based and Hyperbolic Models*  
> *Developed for academic research and educational purposes.*
