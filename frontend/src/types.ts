export interface TocItem {
    title: string;
    level: number;
}

export interface Book {
    id: string;
    isbn: string;
    title: string;
    toc: TocItem[];
    added_at?: string;
}

export interface SearchBookResult {
    id: string;
    isbn: string;
    title: string;
    toc_json?: string;
}


export interface ChapterRef {
    chapter_title: string;
}

export interface RecommendedBook {
    isbn: string;
    title: string;
    summary: string;
    relevant_chapters: ChapterRef[];
}

export interface SearchReport {
    recommendations: RecommendedBook[];
}

export interface SearchResult {
    query: string;
    results_count: number;
    report: SearchReport;
    search_results: SearchBookResult[];
}

export interface BookPreview {
    isbn: string;
    title: string;
    toc: TocItem[];
}
