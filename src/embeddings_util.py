from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
import os

class EmbeddingsUtil:
    def __init__(self, model_path):
        self.model_path = model_path
        self.cuda_device = os.getenv('EMBEDDING_CUDA_DEVICE', 'cuda:0')
    def get(self, sentences):
        
        # GPU code
        tokenizer = AutoTokenizer.from_pretrained(self.model_path, device=self.cuda_device)
        model = AutoModel.from_pretrained(self.model_path, device_map=self.cuda_device)

        # Tokenize sentences
        encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt').to(self.cuda_device)
    

        # CPU code
        # Load model and tokenizer from local directory
        # tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        # model = AutoModel.from_pretrained(self.model_path)

        # Tokenize sentences
        # encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

        # Compute token embeddings
        with torch.no_grad():
            model_output = model(**encoded_input)

        # Perform pooling
        sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])

        # Normalize embeddings
        embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
        return embeddings.tolist()
        
    # Mean Pooling - Take attention mask into account for correct averaging
    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
