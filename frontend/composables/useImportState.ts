export const useImportState = () => {
  const file = useState<File | null>('import-file', () => null);
  const preview = useState<any>('import-preview', () => null);
  const validation = useState<any>('import-validation', () => null);

  const reset = () => {
    file.value = null;
    preview.value = null;
    validation.value = null;
  };

  return {
    file,
    preview,
    validation,
    reset
  };
};
