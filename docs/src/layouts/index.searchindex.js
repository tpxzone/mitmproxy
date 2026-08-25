{{/*
    This file contains the search index and is only loaded on demand (when the user focuses the search field).
*/}}

window.docsSearch = (function(){
    {{ (resources.Get "elasticlunr.min.js").Content | safeJS }}

    /** search index */
    {{- $pages := slice -}}
    {{- range .Site.RegularPages -}}
        {{- $sectionTitle := "" -}}
        {{- with .Site.GetPage (printf "/%s" .Section) -}}
            {{- $sectionTitle = .Title -}}
        {{- end -}}
        {{- $page := dict 
            "title" .Title
            "url" .RelPermalink
            "content" .Plain
            "section" $sectionTitle
        -}}
        {{- $pages = $pages | append $page -}}
    {{- end -}}
    const docs = {{ $pages | jsonify }};

    // Also split on html tags. this is a cheap heuristic, but good enough.
    // 中文相关的两点调整：
    //  1) 中日韩表意文字/假名按单字切分，否则「代理模式」只会成为一个整词，搜「代理」搜不到。
    //  2) 全角标点（。、（）「」等）也当作分隔符。
    const CJK = "\\u3400-\\u4dbf\\u4e00-\\u9fff\\uf900-\\ufaff\\u3040-\\u30ff";
    elasticlunr.tokenizer.setSeperator(
        new RegExp(
            "[\\s\\-.;&_'\"=,()\\u3000-\\u303f\\uff00-\\uff0f\\uff1a-\\uff20\\uff3b-\\uff40\\uff5b-\\uff65]+"
            + "|<[^>]*>"
            + "|(?<=[" + CJK + "])|(?=[" + CJK + "])"
        )
    );

    // elasticlunr 默认的 trimmer 用 \W 裁剪首尾，而 \W 把所有汉字都算作非单词字符，
    // 结果整个中文词会被裁成空串。换成 Unicode 感知的版本。
    elasticlunr.trimmer = function (token) {
        return token
            .replace(/^[^\p{L}\p{N}]+/u, "")
            .replace(/[^\p{L}\p{N}]+$/u, "");
    };
    elasticlunr.Pipeline.registerFunction(elasticlunr.trimmer, "trimmer");

    console.time("building search index");
    // mirrored in build-search-index.js (part 2)
    let searchIndex = elasticlunr(function () {
        this.pipeline.remove(elasticlunr.stemmer);
        this.pipeline.remove(elasticlunr.stopWordFilter);
        this.addField("title");
        this.addField("content");
        this.addField("section");
        this.setRef("url");
    });
    for (let doc of docs) {
        searchIndex.addDoc(doc);
    }
    console.timeEnd("building search index");

    return (term) => searchIndex.search(term, {
        fields: {
            title: {boost: 4},
            content: {boost: 1},
            section: {boost: 2}
        },
        expand: true
    });
})(); 