document.addEventListener("DOMContentLoaded", function () {
    const filter = document.getElementById("tree-filter");
    if (!filter) return;

    const tree = document.getElementById("delete-tree");
    const rootFolder = tree.querySelector(".root-tree");

    function filterFolder(folder, query) {
        let hasMatch = false;
        Array.from(folder.children).filter(function (item) {
            return item.hasAttribute("data-tree-item");
        }).forEach(function (item) {
            if (item.dataset.treeKind === "file") {
                const matches = !query || item.dataset.treeName.toLowerCase().includes(query);
                item.hidden = !matches;
                hasMatch = hasMatch || matches;
                return;
            }

            const folderMatches = filterFolder(item, query);
            item.hidden = !folderMatches;
            if (folderMatches) item.open = true;
            hasMatch = hasMatch || folderMatches;
        });
        return hasMatch;
    }

    filter.addEventListener("input", function () {
        const query = filter.value.trim().toLowerCase();
        filterFolder(rootFolder, query);
        rootFolder.open = true;
        tree.querySelectorAll(".empty").forEach(function (empty) {
            empty.hidden = Boolean(query);
        });
    });
});
