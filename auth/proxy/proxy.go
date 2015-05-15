package main

import (
    "github.com/elazarl/goproxy"
    "github.com/garyburd/redigo/redis"
    "log"
    "net/http"
    "strings"
)

const TOKEN_HEADER = "X-Yacern-Token"
const USERNAME_HEADER = "X-Yacern-User"

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
        token := r.Header.Get(TOKEN_HEADER)
        tokenkey := strings.Join([]string{"token:", token}, "")

        token_ok, err := redis.Bool(c.Do("SISMEMBER", tokenkey, r.Host))

        if err != nil {
            log.Fatal(err)

            return r,goproxy.NewResponse(r,
                    goproxy.ContentTypeText,http.StatusInternalServerError,
                    "Internal error")
        }

        if token_ok {
            ownerkey := strings.Join([]string{"owner:", token}, "")
            username, err := redis.String(c.Do("GET", ownerkey))
            if err != nil {
                log.Fatal(err)

                return r,goproxy.NewResponse(r,
                        goproxy.ContentTypeText,http.StatusInternalServerError,
                        "Internal error")
            }

            delete(r.Header, TOKEN_HEADER)
            r.Header.Set(USERNAME_HEADER, username)

            return r,nil
        } else {
            return r,goproxy.NewResponse(r,
                    goproxy.ContentTypeText,http.StatusForbidden,
                    "Not allowed")
        }

    })

    log.Fatal(http.ListenAndServe(":8080", proxy))
}
