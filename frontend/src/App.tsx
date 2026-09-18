import styles from "./App.module.css";

export function App() {
  return (
    <div className={styles.appShell}>
      <header className={styles.header}>
        <span className={styles.brand}>UtileasyDoc</span>
      </header>

      <main className={styles.main}>
        <h1>Documentos</h1>
        <p>A fundação da aplicação está pronta para receber os módulos.</p>
      </main>
    </div>
  );
}
