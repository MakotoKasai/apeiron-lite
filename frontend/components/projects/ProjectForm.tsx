"use client";

import { useState } from "react";

type ProjectFormProps = {
    onAdd: (title: string, description: string) => void;
};

export function ProjectForm({ onAdd }: ProjectFormProps) {
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");

    return (
        <form onSubmit={(event) => {
            event.preventDefault();
            onAdd(title,description);
            setTitle("");
            setDescription("");
        }}>
            <div>
                <label htmlFor="title>">Title</label>
                <input
                    id="title"
                    type="text"
                    value={title}
                    onChange={(event) => setTitle(event.target.value)}
                    className="border border-gray-500 px-2 py-1"
                    />
            </div>

            <div>
                <label htmlFor="description">Description</label>
                <input
                    id="description"
                    type="text"
                    value={description}
                    onChange={(event) => setDescription(event.target.value)}
                    className="border border-gray-500 px-2 py-1"
                    />
            </div>
            <button type="submit"
                    className="border border-gray-500 px-3 py-1"
            >Add Project</button>
        </form>
    );
}