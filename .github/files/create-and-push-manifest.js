class RockImage {
    constructor (image, arch) {
        this.image = image
        this.arch = arch
    }
   
    async import_image() {
        console.info(`    ⏬ pull image: ${this.image}`)
        await exec.exec("docker", ["pull", this.image])
    }

    async annotate(target) {
        console.info(`    🖌️ annotate manifest: ${target} ${this.arch}`)
        await exec.exec("docker", ["manifest", "annotate", target, this.image, `--arch=${this.arch}`])
    }
}

class RockComponent {
    constructor (name, version) {
        this.name = name
        this.version = version
        this.imageVer = `${this.name}:${this.version}`
        this.images = []
    }

    async create_manifest(target) {
        const archs = this.images.map(i => i.arch)
        const images = this.images.map(i => i.image)
        console.info(`  📄 create manifest: ${target} ${archs.join(",")}`)
        await exec.exec("docker", ["manifest", "create", target, images.join(' ')])
    }

    async push_manifest(target) {
        console.info(`  ⏫ push manifest: ${target}`)
        console.info(`docker manifest push ${target}`)
        await exec.exec("docker", ["manifest", "push", target])
    }

    async craft_manifest(target) {
        for (const image of this.images) {
            await image.import_image()
        }
        const targetImage = `${target.trim('/')}/${this.imageVer}`
        await exec.exec("docker", ["manifest", "rm", targetImage], {ignoreReturnCode: true})
        await this.create_manifest(targetImage)

        for (const image of this.images) {
            await image.annotate(targetImage)
        }
        await this.push_manifest(targetImage)
    }
}

async function main(inputs, rockMetas) {
    const registry = inputs.registry
    const owner = context.repo.owner
    const metas = rockMetas
    const containers = {}
    for (const meta of metas) {
        if (!containers.hasOwnProperty(meta.name)) {
            containers[meta.name] = new RockComponent(meta.name, meta.version)
        }
        containers[meta.name].images.push(new RockImage(meta.image, meta.arch))
    }
    for (const component of Object.values(containers)) {
        console.info(`🖥️  Assemble Multiarch Image: ${component.name}`)
        await component.craft_manifest(`${registry}/${owner}`)
    }
}
