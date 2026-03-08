window.VSLReact = window.VSLReact || {};

(function initLazyRouteLoader(global) {
  const root = global || {};
  const VSLReact = (root.VSLReact = root.VSLReact || {});

  const BUILDER_DEPENDENCY_PATHS = Object.freeze([
    "/ui/js/react/builder_draft_translator.js",
    "/ui/js/react/builder_constraint_controls.js",
    "/ui/js/react/builder_form_schema.js",
    "/ui/js/react/builder_submission_guards.js",
  ]);

  const loadedScriptPaths = new Set();
  const inFlightScriptLoads = new Map();

  function isBuilderDependenciesReady() {
    return Boolean(
      VSLReact.builderDraftTranslator &&
      typeof VSLReact.builderDraftTranslator.draft_to_payload === "function" &&
      VSLReact.builderConstraintControls &&
      typeof VSLReact.builderConstraintControls.deriveBuilderConstraintState === "function" &&
      VSLReact.builderFormSchema &&
      typeof VSLReact.builderFormSchema.getBuilderSectionSchema === "function" &&
      VSLReact.builderSubmissionGuards &&
      typeof VSLReact.builderSubmissionGuards.assertBuilderDraftForTranslation === "function"
    );
  }

  function loadScriptPath(path) {
    if (!path) return Promise.resolve();
    if (loadedScriptPaths.has(path)) return Promise.resolve();
    if (inFlightScriptLoads.has(path)) return inFlightScriptLoads.get(path);

    const promise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = path;
      script.async = true;
      script.onload = () => {
        loadedScriptPaths.add(path);
        inFlightScriptLoads.delete(path);
        resolve();
      };
      script.onerror = () => {
        inFlightScriptLoads.delete(path);
        reject(new Error(`Failed to load script: ${path}`));
      };
      document.head.appendChild(script);
    });

    inFlightScriptLoads.set(path, promise);
    return promise;
  }

  async function ensureBuilderModulesLoaded() {
    if (isBuilderDependenciesReady()) return;
    await Promise.all(BUILDER_DEPENDENCY_PATHS.map((path) => loadScriptPath(path)));
    if (!isBuilderDependenciesReady()) {
      throw new Error("Builder dependencies loaded but required exports are missing.");
    }
  }

  VSLReact.lazyRouteLoader = {
    BUILDER_DEPENDENCY_PATHS,
    isBuilderDependenciesReady,
    ensureBuilderModulesLoaded,
  };
})(window);
