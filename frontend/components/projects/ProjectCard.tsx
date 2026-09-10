import type { Project } from "@/types/Project";

type ProjectCardProps = {
    project: Project;
}

export function ProjectCard({project: project}: ProjectCardProps) {
    return (
        <li>
            <h2>{project.title}</h2>
            <p>{project.description}</p>
        </li>
    )
}