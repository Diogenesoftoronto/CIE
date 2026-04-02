# Build CIE Go binary
FROM golang:1.24-bookworm AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /cie ./cmd/cie

FROM gcr.io/distroless/static-debian12:nonroot
WORKDIR /
COPY --from=build /cie /usr/local/bin/cie
USER nonroot:nonroot
ENTRYPOINT ["/usr/local/bin/cie"]
