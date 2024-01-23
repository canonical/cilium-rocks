async function get_containers(org, package_name) {
    let containers;
    core.info(`Looking up existing containers ${org}/${package_name}`)
    try {
        containers = (await github.rest.packages.getAllPackageVersionsForPackageOwnedByOrg({
            org,
            package_type: "container",
            package_name,
        })).data;
    } catch (e) {
        containers = [];
        console.error(e);
    }
    return containers
}

async function main(rockMetas){
    const owner = context.repo.owner
    const metas = await Promise.all(
        rockMetas.map(
            async meta => {
                const versions = await get_containers(owner, meta.name)
                const rockVersion_ = meta.version + "-ck"
                const patchRev = versions.reduce((partial, v) =>
                    partial + v.metadata.container.tags.filter(t => t.startsWith(rockVersion_)).length, 0
                )
                meta.version = rockVersion_ + patchRev
                core.info(`Number of containers tagged ${owner}/${meta.name}/${meta.version}: ${patchRev}`)
                core.info(`Tagging image ${meta.image} with ${meta.version}`)
                return meta
            }
        ))
    core.setOutput('rock-metas', JSON.stringify(metas))
}