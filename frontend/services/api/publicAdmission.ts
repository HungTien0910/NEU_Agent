import { useApiFetch } from '@/services/api/client';

export type AdmissionQueryResponse = {
  answer: string;
  confidence: 'low' | 'medium' | 'high';
  citations: Array<{
    doc_id: string;
    title: string;
    chunk_id: string;
    page_start: number;
    page_end: number;
    score: number;
  }>;
};

export const queryAdmission = async (question: string, language = 'vi') => {
  const api = useApiFetch();
  return await api<AdmissionQueryResponse>('/public/admission/query', {
    method: 'POST',
    body: { question, language, top_k: 6 }
  });
};
