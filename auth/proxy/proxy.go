package main

import (
    "github.com/elazarl/goproxy"
    "github.com/garyburd/redigo/redis"
    "log"
    "net/http"
    "strings"
)

func main() {
    c, err := redis.Dial("tcp", ":6379")
    if err != nil {
        log.Fatal(err)
        return
    }

    proxy := goproxy.NewProxyHttpServer()
    proxy.Verbose = true

    proxy.OnRequest().DoFunc(
    func(r *http.Request,ctx *goproxy.ProxyCtx)(*http.Request,*http.Response) {
        tokenkey := strings.Join([]string{"token:", r.Header.Get("Token")}, "")

        username, err := redis.String(c.Do("GET", tokenkey))

        if err != nil {
            log.Fatal(err)

            return r,goproxy.NewResponse(r,
                    goproxy.ContentTypeText,http.StatusInternalServerError,
                    "Internal error")
        }


        if username != ""{
            delete(r.Header, "Token")
            r.Header.Set("Username", username)

            return r,nil
        } else {
            return r,goproxy.NewResponse(r,
                    goproxy.ContentTypeText,http.StatusForbidden,
                    "Not allowed")
        }

    })

    log.Fatal(http.ListenAndServe(":8080", proxy))
}

