import { useEffect, useState } from "react";

import { DocumentDetail } from "./components/DocumentDetail";
import { DocumentList } from "./components/DocumentList";
import { UploadDialog } from "./components/UploadDialog";
import styles from "./App.module.css";

function documentIdFromPath() {
  const match = /^\/documents\/(\d+)\/?$/.exec(window.location.pathname);
  return match ? Number(match[1]) : null;
}

export function App() {
  const [documentId, setDocumentId] = useState(documentIdFromPath);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    const syncPath = () => setDocumentId(documentIdFromPath());
    window.addEventListener("popstate", syncPath);
    return () => window.removeEventListener("popstate", syncPath);
  }, []);

  function navigate(id: number | null) {
    window.history.pushState(null, "", id === null ? "/" : `/documents/${id}`);
    setDocumentId(id);
    setNotice(null);
    window.scrollTo(0, 0);
  }

  return (
    <div className={styles.appShell}>
      <header className={styles.header}>
        <div className={styles.headerInner}>
          <a
            className={styles.brand}
            href="/"
            onClick={(event) => {
              event.preventDefault();
              navigate(null);
            }}
          >
            UtileasyDoc
          </a>
          <button
            className="button buttonPrimary"
            onClick={() => setUploadOpen(true)}
          >
            Novo documento
          </button>
        </div>
      </header>

      {documentId === null ? (
        <DocumentList onOpen={navigate} refreshKey={refreshKey} />
      ) : (
        <DocumentDetail
          key={documentId}
          id={documentId}
          onBack={() => navigate(null)}
          notice={notice}
        />
      )}

      {uploadOpen && (
        <UploadDialog
          onClose={() => setUploadOpen(false)}
          onUploaded={(id, alreadyExists) => {
            setUploadOpen(false);
            setRefreshKey((value) => value + 1);
            navigate(id);
            if (alreadyExists) {
              setNotice(
                "Este arquivo já estava cadastrado. Exibindo o documento existente.",
              );
            }
          }}
        />
      )}
    </div>
  );
}
